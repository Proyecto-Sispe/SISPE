package com.sispe.springboot_web.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import com.sispe.springboot_web.dto.FiltrosReporte;

/**
 * Consulta del reporte multitabla. Une en una sola sentencia SQL las tablas
 * Pedido, Mesa, Sesion_Mesa, Persona (mesero), Detalle_Pedido, Menu, Categoria,
 * Detalle_Pedido_Adicion + Adicion, Factura y Factura_has_Metodo_pago + Metodo_pago.
 * Es Java puro (sin Spring) para poder probarla directamente contra la base de datos.
 */
public final class ConsultaMultitabla {

    private ConsultaMultitabla() { }

    /** Una fila del reporte: una línea de pedido con todos los datos de las tablas relacionadas. */
    public record Fila(Long pedidoId, LocalDateTime fecha, String estado, String prioridad, Long mesa,
                       String ubicacionMesa, String cliente, String mesero, String categoria, String producto,
                       Integer cantidad, BigDecimal precioUnitario, BigDecimal subtotal, String adiciones,
                       Long facturaId, BigDecimal totalFactura, String metodoPago) { }

    public record Consulta(String sql, List<Object> parametros) { }

    public record Resumen(int pedidos, int lineas, int unidades, BigDecimal totalLineas, BigDecimal totalFacturado) { }

    private static final String SELECT = """
            SELECT p.id_pedido, p.fecha_pedido, p.estado, p.prioridad, p.id_mesa,
                   m.Ubicacion AS ubicacion,
                   s.nombre_cliente AS cliente,
                   CONCAT_WS(' ', pe.Nom1_usu, pe.Ape1_usu) AS mesero,
                   c.nom_categoria AS categoria,
                   mn.Productos AS producto,
                   d.cantidad, d.valor_venta,
                   d.cantidad * d.valor_venta AS subtotal,
                   (SELECT GROUP_CONCAT(CONCAT(dpa.cantidad, 'x ', a.nombre) ORDER BY a.nombre SEPARATOR ', ')
                      FROM Detalle_Pedido_Adicion dpa
                      JOIN Adicion a ON a.id_adicion = dpa.id_adicion
                     WHERE dpa.id_detalle = d.id_detalle) AS adiciones,
                   f.id_factura, f.Total AS total_factura,
                   (SELECT GROUP_CONCAT(mp.Tipo_pago ORDER BY mp.Tipo_pago SEPARATOR ', ')
                      FROM Factura_has_Metodo_pago fm
                      JOIN Metodo_pago mp ON mp.id_pago = fm.pkfk_metodo_pago
                     WHERE fm.pkfk_n_factura = f.id_factura) AS metodo_pago
              FROM Pedido p
              JOIN Mesa m ON m.id_Mesa = p.id_mesa
              LEFT JOIN Sesion_Mesa s ON s.id_sesion = p.id_sesion_qr
              LEFT JOIN Persona pe ON pe.id_usuario = p.mesero_id_usuario AND pe.pkfk_Tipo_doc = p.mesero_tipo_doc
              LEFT JOIN Detalle_Pedido d ON d.id_pedido = p.id_pedido
              LEFT JOIN Menu mn ON mn.id_menu = d.id_menu
              LEFT JOIN Categoria c ON c.id_categoria = mn.pkfk_id_categoria
              LEFT JOIN Factura f ON f.id_pedido = p.id_pedido
             WHERE 1 = 1
            """;

    /** Arma la sentencia con solo los filtros que vengan informados. Todos los valores van como parámetros (?). */
    public static Consulta construir(FiltrosReporte f, int limite) {
        StringBuilder sql = new StringBuilder(SELECT);
        List<Object> args = new ArrayList<>();
        if (f.getDesde() != null) {
            sql.append(" AND p.fecha_pedido >= ?\n");
            args.add(Timestamp.valueOf(f.getDesde().atStartOfDay()));
        }
        if (f.getHasta() != null) {
            sql.append(" AND p.fecha_pedido < ?\n"); // exclusivo: incluye el día «Hasta» completo
            args.add(Timestamp.valueOf(f.getHasta().plusDays(1).atStartOfDay()));
        }
        if (hay(f.getEstado())) {
            sql.append(" AND p.estado = ?\n");
            args.add(f.getEstado().trim());
        }
        if (hay(f.getPrioridad())) {
            sql.append(" AND p.prioridad = ?\n");
            args.add(f.getPrioridad().trim());
        }
        if (f.getMesa() != null) {
            sql.append(" AND p.id_mesa = ?\n");
            args.add(f.getMesa());
        }
        if (f.getCategoria() != null) {
            sql.append(" AND mn.pkfk_id_categoria = ?\n");
            args.add(f.getCategoria());
        }
        if (f.getProducto() != null) {
            sql.append(" AND d.id_menu = ?\n");
            args.add(f.getProducto());
        }
        if (f.getMetodoPago() != null) {
            sql.append(" AND EXISTS (SELECT 1 FROM Factura_has_Metodo_pago fm2"
                    + " WHERE fm2.pkfk_n_factura = f.id_factura AND fm2.pkfk_metodo_pago = ?)\n");
            args.add(f.getMetodoPago());
        }
        sql.append(" ORDER BY p.fecha_pedido DESC, p.id_pedido DESC, d.id_detalle\n LIMIT ?");
        args.add(limite);
        return new Consulta(sql.toString(), args);
    }

    /** Convierte la fila actual del ResultSet (según las columnas de {@link #SELECT}) en un {@link Fila}. */
    public static Fila mapear(ResultSet rs) throws SQLException {
        Timestamp fecha = rs.getTimestamp("fecha_pedido");
        return new Fila(
                entero(rs, "id_pedido"),
                fecha == null ? null : fecha.toLocalDateTime(),
                rs.getString("estado"),
                rs.getString("prioridad"),
                entero(rs, "id_mesa"),
                rs.getString("ubicacion"),
                rs.getString("cliente"),
                blancoANulo(rs.getString("mesero")),
                rs.getString("categoria"),
                rs.getString("producto"),
                rs.getObject("cantidad") == null ? null : rs.getInt("cantidad"),
                dinero(rs, "valor_venta"),
                dinero(rs, "subtotal"),
                rs.getString("adiciones"),
                entero(rs, "id_factura"),
                dinero(rs, "total_factura"),
                rs.getString("metodo_pago"));
    }

    /** Totales de las filas mostradas. La factura se cuenta una sola vez aunque el pedido tenga varias líneas. */
    public static Resumen resumir(List<Fila> filas) {
        Set<Long> pedidos = new HashSet<>();
        Set<Long> facturas = new HashSet<>();
        int lineas = 0;
        int unidades = 0;
        BigDecimal totalLineas = BigDecimal.ZERO;
        BigDecimal totalFacturado = BigDecimal.ZERO;
        for (Fila fila : filas) {
            pedidos.add(fila.pedidoId());
            if (fila.cantidad() != null) {
                lineas++;
                unidades += fila.cantidad();
            }
            if (fila.subtotal() != null) totalLineas = totalLineas.add(fila.subtotal());
            if (fila.facturaId() != null && facturas.add(fila.facturaId()) && fila.totalFactura() != null) {
                totalFacturado = totalFacturado.add(fila.totalFactura());
            }
        }
        return new Resumen(pedidos.size(), lineas, unidades, totalLineas, totalFacturado);
    }

    private static boolean hay(String texto) {
        return texto != null && !texto.isBlank();
    }

    private static String blancoANulo(String texto) {
        return texto == null || texto.isBlank() ? null : texto;
    }

    private static Long entero(ResultSet rs, String columna) throws SQLException {
        long valor = rs.getLong(columna);
        return rs.wasNull() ? null : valor;
    }

    private static BigDecimal dinero(ResultSet rs, String columna) throws SQLException {
        BigDecimal valor = rs.getBigDecimal(columna);
        return valor == null ? null : valor.setScale(2, RoundingMode.HALF_UP);
    }
}
