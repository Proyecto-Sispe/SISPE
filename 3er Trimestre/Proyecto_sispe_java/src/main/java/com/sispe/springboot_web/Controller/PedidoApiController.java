// Controller/PedidoApiController.java
package com.sispe.springboot_web.Controller;

import com.sispe.springboot_web.Model.Pedido;
import com.sispe.springboot_web.Repository.PedidoRepository;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/pedidos")
public class PedidoApiController {
    private final PedidoRepository pedidos;
    private final com.sispe.springboot_web.Service.PedidoService pedidoService;
    public PedidoApiController(PedidoRepository pedidos, com.sispe.springboot_web.Service.PedidoService pedidoService) {
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