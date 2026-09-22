package com.sispe.springboot_web.Controller;

import com.sispe.springboot_web.Model.Pedido;
import com.sispe.springboot_web.Repository.FacturaRepository;
import com.sispe.springboot_web.Repository.MesaRepository;
import com.sispe.springboot_web.Repository.PedidoRepository;
import com.sispe.springboot_web.Service.PedidoService;
import org.springframework.dao.DataAccessException;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.WebDataBinder;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

@Controller
@RequestMapping("/pedidos")
public class PedidoController {
    private static final String VISTA_FORMULARIO = "pedidos/nuevo";
    private static final String REDIRECT_PEDIDOS = "redirect:/pedidos";
    private static final String ATTR_ERROR = "error";
    private static final String ATTR_OK = "ok";
    private static final Set<String> ESTADOS = Set.of("pendiente", "en_preparacion", "en_camino", "entregado");
    // Deben coincidir con el ENUM de la columna Pedido.prioridad en la base de datos.
    private static final Set<String> PRIORIDADES = Set.of("normal", "urgente");

    private final PedidoRepository pedidos;
    private final PedidoService pedidoService;
    private final FacturaRepository facturas;
    private final MesaRepository mesas;

    public PedidoController(PedidoRepository pedidos, PedidoService pedidoService, FacturaRepository facturas,
                            MesaRepository mesas) {
        this.pedidos = pedidos;
        this.pedidoService = pedidoService;
        this.facturas = facturas;
        this.mesas = mesas;
    }

    /** Evita que un formulario manipulado modifique campos internos (mesero, sesión QR, confirmación...). */
    @InitBinder("pedido")
    void limitarCamposEditables(WebDataBinder binder) {
        binder.setAllowedFields("mesaId", "clienteId", "estado", "prioridad", "observaciones", "tiempoEstimado");
    }

    @GetMapping
    public String index(Model model) {
        model.addAttribute("pedidos", pedidos.findAll());
        return "pedidos/index";
    }

    /** Sin id abre el formulario vacío; con id carga el pedido para editarlo. */
    @GetMapping("/nuevo")
    public String nuevo(@RequestParam(required = false) Long id, Model model, RedirectAttributes attrs) {
        if (id == null) {
            model.addAttribute("pedido", new Pedido());
            return VISTA_FORMULARIO;
        }
        Pedido existente = pedidos.findById(id).orElse(null);
        if (existente == null) {
            attrs.addFlashAttribute(ATTR_ERROR, "El pedido #" + id + " no existe.");
            return REDIRECT_PEDIDOS;
        }
        model.addAttribute("pedido", existente);
        return VISTA_FORMULARIO;
    }

    @PostMapping("/guardar")
    public String guardar(@ModelAttribute("pedido") Pedido pedido, BindingResult binding, Model model,
                          RedirectAttributes attrs) {
        String error = binding.hasErrors() ? "Revisa los datos: hay campos con un formato no válido." : validar(pedido);
        if (error != null) {
            model.addAttribute(ATTR_ERROR, error);
            return VISTA_FORMULARIO;
        }
        pedido.setId(null); // este endpoint solo crea; la edición pasa por /actualizar/{id}
        pedido.setFechaPedido(LocalDateTime.now());
        if (pedido.getEstado() == null || pedido.getEstado().isBlank()) pedido.setEstado("pendiente");
        if (pedido.getPrioridad() == null || pedido.getPrioridad().isBlank()) pedido.setPrioridad("normal");
        try {
            Pedido guardado = pedidos.save(pedido);
            attrs.addFlashAttribute(ATTR_OK, "Pedido #" + guardado.getId() + " registrado correctamente.");
            return REDIRECT_PEDIDOS;
        } catch (DataAccessException ex) {
            model.addAttribute(ATTR_ERROR, "No se pudo guardar el pedido. Verifica los datos e inténtalo de nuevo.");
            return VISTA_FORMULARIO;
        }
    }

    @PostMapping("/actualizar/{id}")
    public String actualizar(@PathVariable Long id, @ModelAttribute("pedido") Pedido formulario, BindingResult binding,
                             Model model, RedirectAttributes attrs) {
        Pedido existente = pedidos.findById(id).orElse(null);
        if (existente == null) {
            attrs.addFlashAttribute(ATTR_ERROR, "El pedido #" + id + " no existe.");
            return REDIRECT_PEDIDOS;
        }
        formulario.setId(id);
        String error = binding.hasErrors() ? "Revisa los datos: hay campos con un formato no válido." : validar(formulario);
        if (error != null) {
            model.addAttribute(ATTR_ERROR, error);
            return VISTA_FORMULARIO;
        }
        try {
            // Un cambio de estado pasa por el servicio: valida transiciones y descuenta inventario al entregar.
            if (!Objects.equals(existente.getEstado(), formulario.getEstado())) {
                pedidoService.cambiarEstado(id, formulario.getEstado());
            }
            // Solo se copian los campos editables; mesero, sesión QR, fecha y confirmación se conservan.
            Pedido actual = pedidos.findById(id).orElseThrow();
            actual.setMesaId(formulario.getMesaId());
            actual.setClienteId(formulario.getClienteId());
            actual.setPrioridad(formulario.getPrioridad());
            actual.setObservaciones(formulario.getObservaciones());
            actual.setTiempoEstimado(formulario.getTiempoEstimado());
            pedidos.save(actual);
            attrs.addFlashAttribute(ATTR_OK, "Pedido #" + id + " actualizado correctamente.");
            return REDIRECT_PEDIDOS;
        } catch (IllegalStateException | IllegalArgumentException ex) {
            model.addAttribute(ATTR_ERROR, ex.getMessage());
            return VISTA_FORMULARIO;
        } catch (DataAccessException ex) {
            model.addAttribute(ATTR_ERROR, "No se pudo actualizar el pedido. Verifica los datos e inténtalo de nuevo.");
            return VISTA_FORMULARIO;
        }
    }

    @PostMapping("/eliminar/{id}")
    public String eliminar(@PathVariable Long id, RedirectAttributes attrs) {
        try {
            pedidos.deleteById(id);
            attrs.addFlashAttribute(ATTR_OK, "Pedido #" + id + " eliminado.");
        } catch (DataAccessException ex) {
            attrs.addFlashAttribute(ATTR_ERROR, "No se puede eliminar el pedido #" + id
                    + " porque tiene registros asociados (por ejemplo pagos o notificaciones).");
        }
        return REDIRECT_PEDIDOS;
    }

    @GetMapping("/entregar")
    public String entregar(Model model) {
        List<Pedido> listos = pedidos.findByEstadoInOrderByFechaPedidoAsc(List.of("en_camino"));
        Map<Long, Long> facturaPorPedido = new HashMap<>();
        for (var p : listos) {
            facturas.findByPedidoId(p.getId()).ifPresent(f -> facturaPorPedido.put(p.getId(), f.getId()));
        }
        model.addAttribute("pedidos", listos);
        model.addAttribute("facturaPorPedido", facturaPorPedido);
        return "pedidos/entregar";
    }

    @PostMapping("/entregar/{id}")
    public String marcarEntregado(@PathVariable Long id, RedirectAttributes attrs) {
        try {
            pedidoService.entregarYDescontarStock(id);
            attrs.addFlashAttribute(ATTR_OK, "Pedido #" + id + " entregado. Stock descontado.");
        } catch (IllegalStateException | IllegalArgumentException ex) {
            attrs.addFlashAttribute(ATTR_ERROR, ex.getMessage());
        }
        return "redirect:/pedidos/entregar";
    }

    /** Devuelve el primer problema encontrado en el formulario, o null si los datos son válidos. */
    private String validar(Pedido p) {
        if (p.getMesaId() == null || p.getMesaId() < 1) return "Indica un número de mesa válido (mayor que cero).";
        if (p.getMesaId() > Integer.MAX_VALUE || !mesas.existsById(p.getMesaId().intValue())) {
            return "La mesa " + p.getMesaId() + " no existe. Créala primero en el módulo Mesas.";
        }
        if (p.getClienteId() != null && p.getClienteId() < 1) return "El documento del cliente debe ser un número positivo.";
        if (p.getEstado() != null && !p.getEstado().isBlank() && !ESTADOS.contains(p.getEstado())) return "El estado seleccionado no es válido.";
        if (p.getPrioridad() != null && !p.getPrioridad().isBlank() && !PRIORIDADES.contains(p.getPrioridad())) return "La prioridad seleccionada no es válida.";
        if (p.getTiempoEstimado() != null && p.getTiempoEstimado() < 0) return "El tiempo estimado no puede ser negativo.";
        return null;
    }
}
