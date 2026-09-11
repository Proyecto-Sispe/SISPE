package com.sispe.springboot_web.Service;

import com.sispe.springboot_web.Model.Pedido;
import com.sispe.springboot_web.Repository.PedidoRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Set;

@Service
public class PedidoService {
    private static final Set<String> ESTADOS = Set.of("pendiente", "en_preparacion", "en_camino", "entregado");
    private final PedidoRepository repository;
    private final SesionMesaService sesionMesaService;
    private final InventarioService inventarioService;

    public PedidoService(PedidoRepository repository, SesionMesaService sesionMesaService, InventarioService inventarioService) {
        this.repository = repository;
        this.sesionMesaService = sesionMesaService;
        this.inventarioService = inventarioService;
    }

    @Transactional
    public Pedido cambiarEstado(Long id, String estado) {
        if (!ESTADOS.contains(estado)) throw new IllegalArgumentException("Estado de pedido no válido");
        Pedido pedido = repository.findById(id).orElseThrow();
        if ("entregado".equals(pedido.getEstado()) && !"entregado".equals(estado)) {
            throw new IllegalStateException("Un pedido entregado no puede retroceder");
        }
        pedido.setEstado(estado);
        if ("en_camino".equals(estado) || "entregado".equals(estado)) {
            pedido.setPrioridad("normal"); // deja de verse "urgente" en el panel de cocina
        }
        Pedido guardado = repository.save(pedido);
        if ("entregado".equals(estado)) {
            sesionMesaService.despacharPedido(id);
        }
        return guardado;
    }

    /** Lo usa el mesero: descuenta stock y marca el pedido como entregado, en una sola transacción. */
    @Transactional
    public Pedido entregarYDescontarStock(Long id) {
        inventarioService.descontarPedido(id);
        return cambiarEstado(id, "entregado");
    }
}