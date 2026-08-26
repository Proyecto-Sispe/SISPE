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
    public CocinaController(PedidoRepository pedidos) { this.pedidos = pedidos; }

    @GetMapping
    public String index(Model model) {
        model.addAttribute("pedidos", pedidos.findByEstadoInOrderByFechaPedidoAsc(
                List.of("pendiente", "en_preparacion", "en_camino")));
        return "cocina/index";
    }

    @PostMapping("/pedido/{id}/estado")
    public String cambiarEstado(@PathVariable Long id, @RequestParam String estado) {
        Pedido pedido = pedidos.findById(id).orElseThrow();
        pedido.setEstado(estado);
        pedidos.save(pedido);
        return "redirect:/cocina";
    }
}
