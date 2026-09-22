package com.sispe.springboot_web.Service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.math.BigDecimal;
import java.sql.Timestamp;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

import org.junit.jupiter.api.Test;

import com.sispe.springboot_web.Service.ConsultaMultitabla.Consulta;
import com.sispe.springboot_web.Service.ConsultaMultitabla.Fila;
import com.sispe.springboot_web.Service.ConsultaMultitabla.Resumen;
import com.sispe.springboot_web.dto.FiltrosReporte;

/**
 * Pruebas de la consulta multitabla de reportes. Solo comprueban el SQL y los parámetros que se
 * arman (no requieren una base de datos); la consulta en sí se validó manualmente contra una base
 * MySQL/MariaDB real con datos de prueba (ver CAMBIOS.md).
 */
class ConsultaMultitablaTest {

    @Test
    void sinFiltrosSoloAplicaElLimite() {
        Consulta consulta = ConsultaMultitabla.construir(new FiltrosReporte(), 500);

        assertFalse(consulta.sql().contains("p.estado = ?"));
        assertEquals(List.of(500), consulta.parametros());
    }

    @Test
    void cadaFiltroInformadoAgregaSuCondicionYSuParametroEnOrden() {
        FiltrosReporte f = new FiltrosReporte();
        f.setDesde(LocalDate.of(2026, 1, 1));
        f.setHasta(LocalDate.of(2026, 1, 31));
        f.setEstado("entregado");
        f.setPrioridad("urgente");
        f.setMesa(3L);
        f.setCategoria(2);
        f.setProducto(7);
        f.setMetodoPago(1);

        Consulta consulta = ConsultaMultitabla.construir(f, 100);

        assertTrue(consulta.sql().contains("p.fecha_pedido >= ?"));
        assertTrue(consulta.sql().contains("p.fecha_pedido < ?"));
        assertTrue(consulta.sql().contains("p.estado = ?"));
        assertTrue(consulta.sql().contains("p.prioridad = ?"));
        assertTrue(consulta.sql().contains("p.id_mesa = ?"));
        assertTrue(consulta.sql().contains("mn.pkfk_id_categoria = ?"));
        assertTrue(consulta.sql().contains("d.id_menu = ?"));
        assertTrue(consulta.sql().contains("Factura_has_Metodo_pago fm2"));
        assertEquals(List.of(
                Timestamp.valueOf(LocalDate.of(2026, 1, 1).atStartOfDay()),
                Timestamp.valueOf(LocalDate.of(2026, 2, 1).atStartOfDay()), // "hasta" es exclusivo: día siguiente
                "entregado", "urgente", 3L, 2, 7, 1, 100), consulta.parametros());
    }

    @Test
    void textosEnBlancoSeIgnoranComoSiNoSeHubieranInformado() {
        FiltrosReporte f = new FiltrosReporte();
        f.setEstado("   ");
        f.setPrioridad("");

        Consulta consulta = ConsultaMultitabla.construir(f, 50);

        assertFalse(consulta.sql().contains("p.estado = ?"));
        assertFalse(consulta.sql().contains("p.prioridad = ?"));
        assertEquals(List.of(50), consulta.parametros());
    }

    @Test
    void unTextoDeFiltroNuncaSeConcatenaAlSqlSiempreVaComoParametro() {
        FiltrosReporte f = new FiltrosReporte();
        f.setEstado("'; DROP TABLE Pedido; --");

        Consulta consulta = ConsultaMultitabla.construir(f, 50);

        assertFalse(consulta.sql().contains("DROP TABLE"), "el valor del filtro no debe aparecer en el texto del SQL");
        assertEquals("'; DROP TABLE Pedido; --", consulta.parametros().get(0));
    }

    @Test
    void resumirCuentaCadaPedidoYCadaFacturaUnaSolaVez() {
        Fila lineaUno = new Fila(1L, LocalDateTime.now(), "entregado", "normal", 1L, "Piso 1", "Ana", "Juan",
                "Hamburguesas", "Clásica", 2, new BigDecimal("16000.00"), new BigDecimal("32000.00"), null,
                10L, new BigDecimal("50000.00"), "Tarjeta");
        Fila lineaDos = new Fila(1L, LocalDateTime.now(), "entregado", "normal", 1L, "Piso 1", "Ana", "Juan",
                "Hamburguesas", "Soleada", 1, new BigDecimal("18000.00"), new BigDecimal("18000.00"), null,
                10L, new BigDecimal("50000.00"), "Tarjeta"); // misma factura que la línea anterior
        Fila otroPedido = new Fila(2L, LocalDateTime.now(), "pendiente", "urgente", 2L, "Piso 2", null, null,
                "Pizza", "Hawaiana", 1, new BigDecimal("20000.00"), new BigDecimal("20000.00"), null,
                null, null, null); // sin factura todavía

        Resumen resumen = ConsultaMultitabla.resumir(List.of(lineaUno, lineaDos, otroPedido));

        assertEquals(2, resumen.pedidos());
        assertEquals(3, resumen.lineas());
        assertEquals(4, resumen.unidades());
        assertEquals(new BigDecimal("70000.00"), resumen.totalLineas());
        assertEquals(new BigDecimal("50000.00"), resumen.totalFacturado(), "la factura 10 no debe sumarse dos veces");
    }

    @Test
    void resumirUnaListaVaciaDaTotalesEnCero() {
        Resumen resumen = ConsultaMultitabla.resumir(List.of());

        assertEquals(0, resumen.pedidos());
        assertEquals(0, resumen.lineas());
        assertEquals(0, resumen.unidades());
        assertEquals(BigDecimal.ZERO, resumen.totalLineas());
        assertEquals(BigDecimal.ZERO, resumen.totalFacturado());
    }
}
