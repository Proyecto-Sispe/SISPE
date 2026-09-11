package com.sispe.springboot_web.Service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.when;
import static org.mockito.Mockito.lenient;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.sispe.springboot_web.Model.DetallePedido;
import com.sispe.springboot_web.Model.Factura;
import com.sispe.springboot_web.Model.Insumo;
import com.sispe.springboot_web.Model.Menu;
import com.sispe.springboot_web.Model.Pedido;
import com.sispe.springboot_web.Repository.DetallePedidoRepository;
import com.sispe.springboot_web.Repository.FacturaRepository;
import com.sispe.springboot_web.Repository.InsumoRepository;
import com.sispe.springboot_web.Repository.PedidoRepository;

@ExtendWith(MockitoExtension.class)
class ReporteServiceTest {

    @Mock
    private PedidoRepository pedidos;

    @Mock
    private FacturaRepository facturas;

    @Mock
    private InsumoRepository insumos;

    @Mock
    private DetallePedidoRepository detalles;

    private ReporteService reporteService;
    private Pedido pedido;
    private Factura factura;
    private DetallePedido detalle;
    private Insumo insumo;

    @BeforeEach
    void setUp() {
        reporteService = new ReporteService(pedidos, facturas, insumos, detalles);
        pedido = Pedido.builder()
                .id(1L)
                .mesaId(3L)
                .meseroId(20L)
                .fechaPedido(LocalDateTime.of(2026, 9, 10, 12, 0))
                .estado("entregado")
                .prioridad("normal")
                .build();
        factura = Factura.builder()
                .id(7L)
                .pedidoId(1L)
                .fechaHora(pedido.getFechaPedido())
                .total(new BigDecimal("25000"))
                .build();
        Menu menu = Menu.builder().id(4).producto("Hamburguesa").build();
        detalle = DetallePedido.builder()
                .pedidoId(1L)
                .menu(menu)
                .cantidad(2)
                .valorVenta(new BigDecimal("12500"))
                .build();
        insumo = Insumo.builder()
                .id(2L)
                .nombre("Queso")
                .stockActual(new BigDecimal("10"))
                .stockMinimo(new BigDecimal("5"))
                .unidad("Kg")
                .build();
        lenient().when(pedidos.findAll()).thenReturn(List.of(pedido));
        lenient().when(facturas.findAll()).thenReturn(List.of(factura));
        lenient().when(detalles.findAll()).thenReturn(List.of(detalle));
        lenient().when(insumos.findAll()).thenReturn(List.of(insumo));
    }

    @Test
    void datosFiltraPorFechaEstadoYRelacionaFacturas() {
        Map<String, Object> resultado = reporteService.datos(
                LocalDate.of(2026, 9, 1), LocalDate.of(2026, 9, 30), "ENTREGADO");

        assertEquals(List.of(pedido), resultado.get("pedidos"));
        assertEquals(List.of(factura), resultado.get("facturas"));
        assertEquals(List.of(detalle), resultado.get("detalles"));
        assertEquals(new BigDecimal("25000"), resultado.get("totalVentas"));
        assertEquals(1, resultado.get("totalPedidos"));
    }

    @Test
    void datosExcluyePedidoFueraDeRangoOConEstadoDistinto() {
        Map<String, Object> fueraDeRango = reporteService.datos(
                LocalDate.of(2026, 10, 1), null, null);
        Map<String, Object> estadoDistinto = reporteService.datos(null, null, "pendiente");

        assertTrue(((List<?>) fueraDeRango.get("pedidos")).isEmpty());
        assertTrue(((List<?>) estadoDistinto.get("pedidos")).isEmpty());
        assertEquals(BigDecimal.ZERO, fueraDeRango.get("totalVentas"));
    }

    @Test
    void generaPdfParaCadaTipoYParaTipoDesconocido() {
        Map<String, Object> datos = reporteService.datos(null, null, null);

        for (String tipo : List.of("general", "producto", "usuarios", "ventas", "inventario", "otro")) {
            byte[] pdf = reporteService.pdf(tipo, datos);
            assertTrue(pdf.length > 0, "El PDF debe tener contenido para " + tipo);
        }
    }

    @Test
    void generaPdfConListasVaciasYValoresNulos() {
        Pedido pedidoSinFecha = Pedido.builder().id(2L).mesaId(1L).estado(null).prioridad(null).build();
        DetallePedido detalleNulo = DetallePedido.builder().pedidoId(2L).cantidad(null).valorVenta(null).build();
        Insumo insumoNulo = Insumo.builder().nombre("Sin stock").build();
        Map<String, Object> datos = Map.of(
                "pedidos", List.of(pedidoSinFecha),
                "detalles", List.of(detalleNulo),
                "facturas", List.of(Factura.builder().pedidoId(2L).build()),
                "insumos", List.of(insumoNulo),
                "totalPedidos", 1,
                "totalVentas", BigDecimal.ZERO);

        assertTrue(reporteService.pdf("producto", datos).length > 0);
        assertTrue(reporteService.pdf("usuarios", datos).length > 0);
        assertTrue(reporteService.pdf("ventas", datos).length > 0);
        assertTrue(reporteService.pdf("inventario", datos).length > 0);
        assertTrue(reporteService.pdf("general", Map.of("pedidos", List.of(), "totalPedidos", 0, "totalVentas", BigDecimal.ZERO)).length > 0);
    }
}
