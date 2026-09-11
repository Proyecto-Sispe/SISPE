package com.sispe.springboot_web.Service;

import com.sispe.springboot_web.Model.*;
import com.sispe.springboot_web.Repository.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class FacturaService {
    private final FacturaRepository facturas;
    private final FacturaMetodoPagoRepository facturaMetodoPagos;
    private final MetodoPagoRepository metodosPago;
    private final DetallePedidoRepository detalles;
    private final DetallePedidoAdicionRepository detalleAdiciones;
    private final PedidoRepository pedidos;

    @Transactional
    public Factura confirmarPago(Long pedidoId, Integer metodoPagoId) {
        Pedido pedido = pedidos.findById(pedidoId).orElseThrow();
        if (Boolean.TRUE.equals(pedido.getConfirmado())) {
            throw new IllegalStateException("Este pedido ya fue confirmado y pagado.");
        }

        List<DetallePedido> items = detalles.findByPedidoId(pedidoId);
        if (items.isEmpty()) {
            throw new IllegalStateException("No puedes pagar un pedido vacío.");
        }

        // El total real = (precio x cantidad) de cada producto + sus adiciones.
        BigDecimal total = BigDecimal.ZERO;
        for (DetallePedido item : items) {
            BigDecimal subtotal = item.getValorVenta().multiply(BigDecimal.valueOf(item.getCantidad()));
            for (DetallePedidoAdicion extra : detalleAdiciones.findByDetallePedido_Id(item.getId())) {
                subtotal = subtotal.add(extra.getAdicion().getPrecio().multiply(BigDecimal.valueOf(extra.getCantidad())));
            }
            total = total.add(subtotal);
        }

        Factura factura = facturas.findByPedidoId(pedidoId)
                .orElseThrow(() -> new IllegalStateException("No existe factura para este pedido."));
        factura.setTotal(total);
        factura.setFechaHora(LocalDateTime.now());
        facturas.save(factura);

        MetodoPago metodo = metodosPago.findById(metodoPagoId)
                .orElseThrow(() -> new IllegalArgumentException("Método de pago no válido"));
        FacturaMetodoPago pago = FacturaMetodoPago.builder()
                .id(new FacturaMetodoPagoId(factura.getId(), metodo.getId()))
                .factura(factura)
                .metodoPago(metodo)
                .monto(total)
                .build();
        facturaMetodoPagos.save(pago);

        // Bloquea el carrito: ya no se pueden agregar más productos.
        pedido.setConfirmado(true);
        pedidos.save(pedido);

        return factura;
    }
}