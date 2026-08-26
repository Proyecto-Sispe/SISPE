package com.login.demo.service;

import com.login.demo.model.Pedido;
import com.login.demo.repository.PedidoRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Set;

@Service
public class PedidoService {
    private static final Set<String> ESTADOS = Set.of("pendiente", "en_preparacion", "en_camino", "entregado");
    private final PedidoRepository repository;

    public PedidoService(PedidoRepository repository) { this.repository = repository; }

    @Transactional
    public Pedido cambiarEstado(Long id, String estado) {
        if (!ESTADOS.contains(estado)) throw new IllegalArgumentException("Estado de pedido no válido");
        Pedido pedido = repository.findById(id).orElseThrow();
        if ("entregado".equals(pedido.getEstado()) && !"entregado".equals(estado)) {
            throw new IllegalStateException("Un pedido entregado no puede retroceder");
        }
        pedido.setEstado(estado);
        return repository.save(pedido);
    }
}
