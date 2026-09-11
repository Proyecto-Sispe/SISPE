package com.sispe.springboot_web.Controller;

import java.math.BigDecimal;
import java.util.List;

import org.springframework.dao.DataAccessException;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import com.sispe.springboot_web.Model.Adicion;
import com.sispe.springboot_web.Model.DetallePedido;
import com.sispe.springboot_web.Model.DetallePedidoAdicion;
import com.sispe.springboot_web.Model.Menu;
import com.sispe.springboot_web.Model.Mesa;
import com.sispe.springboot_web.Model.Pedido;
import com.sispe.springboot_web.Repository.AdicionRepository;
import com.sispe.springboot_web.Repository.DetallePedidoAdicionRepository;
import com.sispe.springboot_web.Repository.DetallePedidoRepository;
import com.sispe.springboot_web.Repository.MenuRepository;
import com.sispe.springboot_web.Repository.MesaRepository;
import com.sispe.springboot_web.Repository.MetodoPagoRepository;
import com.sispe.springboot_web.Repository.PedidoRepository;
import com.sispe.springboot_web.Service.FacturaService;
import com.sispe.springboot_web.Service.SesionMesaService;

import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;

@Controller
@RequiredArgsConstructor
@RequestMapping("/cliente")
public class ClienteController {
    private final MenuRepository menuRepository;
    private final MesaRepository mesaRepository;
    private final DetallePedidoRepository detalleRepository;
    private final DetallePedidoAdicionRepository detalleAdicionRepository;
    private final AdicionRepository adicionRepository;
    private final MetodoPagoRepository metodoPagoRepository;
    private final PedidoRepository pedidoRepository;
    private final SesionMesaService sesionMesaService;
    private final FacturaService facturaService;

    @GetMapping("/escanear/{idMesa}")
    public String formularioEscaneo(@PathVariable Integer idMesa, Model model) {
        Mesa mesa = mesaRepository.findById(idMesa).orElseThrow();
        model.addAttribute("mesa", mesa);
        return "cliente/escanear";
    }

    @PostMapping("/escanear/{idMesa}")
    public String registrarEnMesa(@PathVariable Integer idMesa, @RequestParam String nombre,
                                   @RequestParam Integer cedula, HttpSession session,
                                   RedirectAttributes attrs) {
        try {
            Long idPedido = sesionMesaService.registrarClienteYCrearPedido(idMesa, nombre, cedula);
            session.setAttribute("pedidoActivoId", idPedido);
            session.setAttribute("mesaActivaId", idMesa);
            return "redirect:/menu/digital";
        } catch (DataAccessException ex) {
            attrs.addFlashAttribute("error", "Esta mesa ya está ocupada. Avisa a un mesero.");
            return "redirect:/cliente/escanear/" + idMesa;
        }
    }

    @GetMapping("/carrito/agregar")
    public String formularioAgregar() {
        return "redirect:/menu/digital";
    }

    @PostMapping("/carrito/agregar")
    public String agregar(@RequestParam Integer productoId,
                           @RequestParam(defaultValue = "1") Integer cantidad,
                           @RequestParam(required = false) String observaciones,
                           @RequestParam(required = false, name = "adicionesIds") List<Long> adicionesIds,
                           HttpSession session, RedirectAttributes attrs) {
        Long idPedido = (Long) session.getAttribute("pedidoActivoId");
        if (idPedido == null) {
            attrs.addFlashAttribute("error", "Escanea el código QR de tu mesa antes de pedir.");
            return "redirect:/menu/digital";
        }
        if (pedidoRepository.findById(idPedido).map(Pedido::getConfirmado).orElse(false)) {
            attrs.addFlashAttribute("error", "Tu pedido ya fue enviado a cocina, no puedes agregar más productos.");
            return "redirect:/cliente/pedido";
        }
        if (cantidad == null || cantidad < 1) cantidad = 1;

        Menu producto = menuRepository.findById(productoId).orElseThrow();
        DetallePedido detalle = DetallePedido.builder()
                .pedidoId(idPedido)
                .menu(producto)
                .cantidad(cantidad)
                .valorVenta(producto.getPrecio())
                .observaciones(observaciones)
                .build();
        detalle = detalleRepository.save(detalle);

        if (adicionesIds != null) {
            for (Long adicionId : adicionesIds) {
                Adicion adicion = adicionRepository.findById(adicionId).orElse(null);
                if (adicion == null) continue;
                detalleAdicionRepository.save(DetallePedidoAdicion.builder()
                        .detallePedido(detalle)
                        .adicion(adicion)
                        .cantidad(1)
                        .build());
            }
        }
        return "redirect:/menu/digital";
    }

    @PostMapping("/carrito/eliminar/{idDetalle}")
    public String eliminarItem(@PathVariable Long idDetalle, HttpSession session, RedirectAttributes attrs) {
        Long idPedido = (Long) session.getAttribute("pedidoActivoId");
        DetallePedido detalle = detalleRepository.findById(idDetalle).orElse(null);
        if (detalle == null || idPedido == null || !detalle.getPedidoId().equals(idPedido)) {
            attrs.addFlashAttribute("error", "Ese producto no pertenece a tu pedido.");
            return "redirect:/cliente/pedido";
        }
        detalleAdicionRepository.deleteByDetallePedido_Id(idDetalle);
        detalleRepository.deleteById(idDetalle);
        return "redirect:/cliente/pedido";
    }

    @GetMapping("/pedido")
    public String pedido(HttpSession session, Model model) {
        Long idPedido = (Long) session.getAttribute("pedidoActivoId");
        List<DetallePedido> items = idPedido == null ? List.of() : detalleRepository.findByPedidoId(idPedido);

        BigDecimal total = BigDecimal.ZERO;
        for (DetallePedido item : items) {
            BigDecimal subtotal = item.getValorVenta().multiply(BigDecimal.valueOf(item.getCantidad()));
            for (DetallePedidoAdicion extra : detalleAdicionRepository.findByDetallePedido_Id(item.getId())) {
                subtotal = subtotal.add(extra.getAdicion().getPrecio().multiply(BigDecimal.valueOf(extra.getCantidad())));
            }
            total = total.add(subtotal);
        }

        boolean confirmado = idPedido != null
                && pedidoRepository.findById(idPedido).map(Pedido::getConfirmado).orElse(false);

        model.addAttribute("items", items);
        model.addAttribute("adicionesPorDetalle", detalleAdicionRepository);
        model.addAttribute("total", total);
        model.addAttribute("confirmado", confirmado);
        return "cliente/pedido";
    }

    @PostMapping("/carrito/vaciar")
    public String vaciar(HttpSession session) {
        Long idPedido = (Long) session.getAttribute("pedidoActivoId");
        if (idPedido != null) detalleRepository.deleteByPedidoId(idPedido);
        return "redirect:/cliente/pedido";
    }

    @GetMapping("/pago")
    public String pago(HttpSession session, Model model, RedirectAttributes attrs) {
        Long idPedido = (Long) session.getAttribute("pedidoActivoId");
        List<DetallePedido> items = idPedido == null ? List.of() : detalleRepository.findByPedidoId(idPedido);
        if (items.isEmpty()) {
            attrs.addFlashAttribute("error", "Agrega al menos un producto antes de pagar.");
            return "redirect:/menu/digital";
        }
        BigDecimal total = BigDecimal.ZERO;
        for (DetallePedido item : items) {
            BigDecimal subtotal = item.getValorVenta().multiply(BigDecimal.valueOf(item.getCantidad()));
            for (DetallePedidoAdicion extra : detalleAdicionRepository.findByDetallePedido_Id(item.getId())) {
                subtotal = subtotal.add(extra.getAdicion().getPrecio().multiply(BigDecimal.valueOf(extra.getCantidad())));
            }
            total = total.add(subtotal);
        }
        model.addAttribute("total", total);
        model.addAttribute("metodos", metodoPagoRepository.findAll());
        return "cliente/pago";
    }

    @PostMapping("/pago/confirmar")
    public String confirmarPago(@RequestParam Integer metodoPagoId, HttpSession session, RedirectAttributes attrs) {
        Long idPedido = (Long) session.getAttribute("pedidoActivoId");
        if (idPedido == null) {
            attrs.addFlashAttribute("error", "No hay un pedido activo.");
            return "redirect:/menu/digital";
        }
        try {
            facturaService.confirmarPago(idPedido, metodoPagoId);
            return "redirect:/cliente/estado";
        } catch (IllegalStateException | IllegalArgumentException ex) {
            attrs.addFlashAttribute("error", ex.getMessage());
            return "redirect:/cliente/pago";
        }
    }

    @GetMapping("/estado")
    public String estado(HttpSession session, Model model) {
        Long idPedido = (Long) session.getAttribute("pedidoActivoId");
        Pedido pedido = idPedido == null ? null : pedidoRepository.findById(idPedido).orElse(null);
        model.addAttribute("pedido", pedido);
        return "cliente/estado";
    }
}