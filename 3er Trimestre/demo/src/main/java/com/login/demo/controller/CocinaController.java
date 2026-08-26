package com.login.demo.controller;

import com.login.demo.model.Pedido;
import com.login.demo.repository.PedidoRepository;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@Controller
@RequestMapping("/cocina")
public class CocinaController {
    private final PedidoRepository pedidos;
    private final com.login.demo.service.PedidoService pedidoService;
    public CocinaController(PedidoRepository pedidos, com.login.demo.service.PedidoService pedidoService) {
        this.pedidos = pedidos;
        this.pedidoService = pedidoService;
    }

    @GetMapping
    public String index(Model model) {
        model.addAttribute("pedidos", pedidos.findByEstadoInOrderByFechaPedidoAsc(
                List.of("pendiente", "en_preparacion", "en_camino")));
        return "cocina/index";
    }

    @PostMapping("/pedido/{id}/estado")
    public String cambiarEstado(@PathVariable Long id, @RequestParam String estado) {
        pedidoService.cambiarEstado(id, estado);
        return "redirect:/cocina";
    }
}
