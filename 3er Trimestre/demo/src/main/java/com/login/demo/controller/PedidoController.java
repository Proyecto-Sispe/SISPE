package com.login.demo.controller;

import com.login.demo.repository.PedidoRepository;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDateTime;

@Controller
@RequestMapping("/pedidos")
public class PedidoController {
    private final PedidoRepository pedidos;
    public PedidoController(PedidoRepository pedidos) { this.pedidos = pedidos; }
    @GetMapping
    public String index(Model model) {
        model.addAttribute("pedidos", pedidos.findAll());
        return "pedidos/index";
    }

    @GetMapping("/nuevo")
    public String nuevo(Model model) { model.addAttribute("pedido", new com.login.demo.model.Pedido()); return "pedidos/nuevo"; }

    @PostMapping("/guardar")
    public String guardar(@ModelAttribute com.login.demo.model.Pedido pedido) {
        if (pedido.getFechaPedido() == null) pedido.setFechaPedido(LocalDateTime.now());
        if (pedido.getEstado() == null || pedido.getEstado().isBlank()) pedido.setEstado("pendiente");
        if (pedido.getPrioridad() == null || pedido.getPrioridad().isBlank()) pedido.setPrioridad("normal");
        pedidos.save(pedido); return "redirect:/pedidos";
    }

    @PostMapping("/actualizar/{id}")
    public String actualizar(@PathVariable Long id, @ModelAttribute com.login.demo.model.Pedido pedido) { pedido.setId(id); return guardar(pedido); }

    @PostMapping("/eliminar/{id}")
    public String eliminar(@PathVariable Long id) { pedidos.deleteById(id); return "redirect:/pedidos"; }
}
