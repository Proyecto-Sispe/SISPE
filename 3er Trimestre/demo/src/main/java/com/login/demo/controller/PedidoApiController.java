package com.login.demo.controller;

import com.login.demo.model.Pedido;
import com.login.demo.repository.PedidoRepository;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/pedidos")
public class PedidoApiController {
    private final PedidoRepository pedidos;
    private final com.login.demo.service.PedidoService pedidoService;
    public PedidoApiController(PedidoRepository pedidos, com.login.demo.service.PedidoService pedidoService) {
        this.pedidos = pedidos;
        this.pedidoService = pedidoService;
    }
    @GetMapping public List<Pedido> listar() { return pedidos.findAll(); }
    @GetMapping("/{id}") public Pedido obtener(@PathVariable Long id) { return pedidos.findById(id).orElseThrow(); }
    @PostMapping @ResponseStatus(HttpStatus.CREATED) public Pedido crear(@RequestBody Pedido pedido) { return pedidos.save(pedido); }
    @PatchMapping("/{id}/estado") public Pedido estado(@PathVariable Long id, @RequestParam String valor) {
        return pedidoService.cambiarEstado(id, valor);
    }
}
