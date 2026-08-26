package com.login.demo.controller;

import com.login.demo.repository.PedidoRepository;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

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
    public String nuevo() { return "pedidos/nuevo"; }
}
