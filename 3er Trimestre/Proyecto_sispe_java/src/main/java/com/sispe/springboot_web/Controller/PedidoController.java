package com.sispe.springboot_web.Controller;

import com.sispe.springboot_web.Repository.FacturaRepository;
import com.sispe.springboot_web.Repository.PedidoRepository;
import com.sispe.springboot_web.Service.PedidoService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Controller
@RequestMapping("/pedidos")
public class PedidoController {
    private final PedidoRepository pedidos;
    private final PedidoService pedidoService;
    private final FacturaRepository facturas;

    public PedidoController(PedidoRepository pedidos, PedidoService pedidoService, FacturaRepository facturas) {
        this.pedidos = pedidos;
        this.pedidoService = pedidoService;
        this.facturas = facturas;
    }

    @GetMapping
    public String index(Model model) {
        model.addAttribute("pedidos", pedidos.findAll());
        return "pedidos/index";
    }

    @GetMapping("/nuevo")
    public String nuevo(Model model) { model.addAttribute("pedido", new com.sispe.springboot_web.Model.Pedido()); return "pedidos/nuevo"; }

    @PostMapping("/guardar")
    public String guardar(@ModelAttribute com.sispe.springboot_web.Model.Pedido pedido) {
        if (pedido.getFechaPedido() == null) pedido.setFechaPedido(LocalDateTime.now());
        if (pedido.getEstado() == null || pedido.getEstado().isBlank()) pedido.setEstado("pendiente");
        if (pedido.getPrioridad() == null || pedido.getPrioridad().isBlank()) pedido.setPrioridad("normal");
        pedidos.save(pedido); return "redirect:/pedidos";
    }

    @PostMapping("/actualizar/{id}")
    public String actualizar(@PathVariable Long id, @ModelAttribute com.sispe.springboot_web.Model.Pedido pedido) { pedido.setId(id); return guardar(pedido); }

    @PostMapping("/eliminar/{id}")
    public String eliminar(@PathVariable Long id) { pedidos.deleteById(id); return "redirect:/pedidos"; }

    @GetMapping("/entregar")
    public String entregar(Model model) {
        List<com.sispe.springboot_web.Model.Pedido> listos =
                pedidos.findByEstadoInOrderByFechaPedidoAsc(List.of("en_camino"));
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
            attrs.addFlashAttribute("ok", "Pedido #" + id + " entregado. Stock descontado.");
        } catch (IllegalStateException ex) {
            attrs.addFlashAttribute("error", ex.getMessage());
        }
        return "redirect:/pedidos/entregar";
    }
}