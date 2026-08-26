package com.login.demo.controller;

import com.login.demo.repository.FacturaRepository;
import com.login.demo.repository.PedidoRepository;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.RequestParam;

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
    public String index(@RequestParam(required = false) String estado,
                        @RequestParam(required = false) Long mesa,
                        @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate desde,
                        @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate hasta,
                        Model model) {
        var pedidosListado = pedidos.findAll().stream()
                .filter(p -> estado == null || estado.isBlank() || estado.equalsIgnoreCase(p.getEstado()))
                .filter(p -> mesa == null || mesa.equals(p.getMesaId()))
                .filter(p -> desde == null || (p.getFechaPedido() != null && !p.getFechaPedido().isBefore(desde.atStartOfDay())))
                .filter(p -> hasta == null || (p.getFechaPedido() != null && p.getFechaPedido().isBefore(hasta.plusDays(1).atStartOfDay())))
                .toList();
        model.addAttribute("estadoFiltro", estado); model.addAttribute("mesaFiltro", mesa); model.addAttribute("desde", desde); model.addAttribute("hasta", hasta);
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
