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

    public PedidoService(PedidoRepository repository, SesionMesaService sesionMesaService) {
        this.repository = repository;
        this.sesionMesaService = sesionMesaService;
    }

    @Transactional
    public Pedido cambiarEstado(Long id, String estado) {
        if (!ESTADOS.contains(estado)) throw new IllegalArgumentException("Estado de pedido no válido");
        Pedido pedido = repository.findById(id).orElseThrow();
        if ("entregado".equals(pedido.getEstado()) && !"entregado".equals(estado)) {
            throw new IllegalStateException("Un pedido entregado no puede retroceder");
        }
        pedido.setEstado(estado);
        Pedido guardado = repository.save(pedido);
        if ("entregado".equals(estado)) {
            sesionMesaService.despacharPedido(id);
        }
        return guardado;
    }
}