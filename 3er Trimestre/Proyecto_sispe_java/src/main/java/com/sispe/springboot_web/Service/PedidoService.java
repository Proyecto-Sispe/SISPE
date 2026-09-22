package com.sispe.springboot_web.Service;

import com.sispe.springboot_web.Model.Pedido;
import com.sispe.springboot_web.Repository.PedidoRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Set;

@Service
public class PedidoService {
    private static final String ENTREGADO = "entregado";
    private static final Set<String> ESTADOS = Set.of("pendiente", "en_preparacion", "en_camino", ENTREGADO);
    private final PedidoRepository repository;
    private final SesionMesaService sesionMesaService;
    private final InventarioService inventarioService;

    public PedidoService(PedidoRepository repository, SesionMesaService sesionMesaService, InventarioService inventarioService) {
        this.repository = repository;
        this.sesionMesaService = sesionMesaService;
        this.inventarioService = inventarioService;
    }

    /**
     * Cambia el estado de un pedido. El descuento de inventario está ligado a la transición
     * hacia "entregado", de modo que ocurre una sola vez sin importar desde dónde se marque
     * (panel de cocina, vista del mesero o API). Todo va en la misma transacción: si no hay
     * stock suficiente, el pedido conserva su estado anterior.
     */
    @Transactional
    public Pedido cambiarEstado(Long id, String estado) {
        if (estado == null || !ESTADOS.contains(estado)) throw new IllegalArgumentException("Estado de pedido no válido");
        Pedido pedido = repository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("El pedido #" + id + " no existe"));
        boolean yaEntregado = ENTREGADO.equals(pedido.getEstado());
        if (yaEntregado && !ENTREGADO.equals(estado)) {
            throw new IllegalStateException("Un pedido entregado no puede retroceder");
        }
        if (ENTREGADO.equals(estado) && !yaEntregado) {
            inventarioService.descontarPedido(id);
        }
        pedido.setEstado(estado);
        if ("en_camino".equals(estado) || ENTREGADO.equals(estado)) {
            pedido.setPrioridad("normal"); // deja de verse "urgente" en el panel de cocina
        }
        Pedido guardado = repository.save(pedido);
        if (ENTREGADO.equals(estado) && !yaEntregado) {
            sesionMesaService.despacharPedido(id);
        }
        return guardado;
    }

    /** Lo usa el mesero: marca el pedido como entregado; el descuento de stock va incluido en la transición. */
    @Transactional
    public Pedido entregarYDescontarStock(Long id) {
        return cambiarEstado(id, ENTREGADO);
    }
}
