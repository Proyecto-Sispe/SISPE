package com.login.demo.controller;

import com.login.demo.repository.FacturaRepository;
import com.login.demo.repository.PedidoRepository;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

import java.math.BigDecimal;

@Controller
@RequestMapping("/reportes")
public class ReporteController {
    private final PedidoRepository pedidos;
    private final FacturaRepository facturas;

    public ReporteController(PedidoRepository pedidos, FacturaRepository facturas) {
        this.pedidos = pedidos;
        this.facturas = facturas;
    }

    @GetMapping
    public String index(Model model) {
        var pedidosListado = pedidos.findAll();
        var facturasListado = facturas.findAll();
        var total = facturasListado.stream().map(f -> f.getTotal() == null ? BigDecimal.ZERO : f.getTotal())
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        model.addAttribute("pedidos", pedidosListado);
        model.addAttribute("facturas", facturasListado);
        model.addAttribute("totalVentas", total);
        model.addAttribute("totalPedidos", pedidosListado.size());
        return "reportes/index";
    }
}
