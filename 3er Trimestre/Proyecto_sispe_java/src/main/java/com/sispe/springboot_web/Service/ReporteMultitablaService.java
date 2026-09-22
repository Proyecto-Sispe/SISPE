package com.sispe.springboot_web.Service;

import java.io.ByteArrayOutputStream;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

import javax.sql.DataSource;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import com.lowagie.text.Document;
import com.lowagie.text.Element;
import com.lowagie.text.Font;
import com.lowagie.text.FontFactory;
import com.lowagie.text.PageSize;
import com.lowagie.text.Paragraph;
import com.lowagie.text.Phrase;
import com.lowagie.text.pdf.PdfPCell;
import com.lowagie.text.pdf.PdfPTable;
import com.lowagie.text.pdf.PdfWriter;
import com.sispe.springboot_web.Service.ConsultaMultitabla.Fila;
import com.sispe.springboot_web.Service.ConsultaMultitabla.Resumen;
import com.sispe.springboot_web.dto.FiltrosReporte;

/**
 * Reporte multitabla: consulta la base de datos con joins entre pedidos, mesas, clientes, meseros,
 * productos, categorías, adiciones, facturas y métodos de pago, y lo entrega en pantalla, PDF o Excel.
 */
@Service
public class ReporteMultitablaService {

    /** Máximo de filas que se muestran en pantalla. */
    public static final int MAX_PANTALLA = 500;
    /** Máximo de filas que se exportan a PDF o Excel. */
    public static final int MAX_EXPORTACION = 20_000;

    private static final DateTimeFormatter FECHA_HORA = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm");
    private static final Font TITULO = FontFactory.getFont(FontFactory.HELVETICA_BOLD, 15);
    private static final Font CABECERA = FontFactory.getFont(FontFactory.HELVETICA_BOLD, 8);
    private static final Font CELDA = FontFactory.getFont(FontFactory.HELVETICA, 8);

    /** Opción de una lista desplegable (categoría, producto o método de pago). */
    public record Opcion(Integer id, String nombre) { }

    /** Resultado de una consulta: filas (recortadas al límite), si hubo más, y los totales. */
    public record Resultado(List<Fila> filas, boolean truncado, Resumen resumen) { }

    private final JdbcTemplate jdbc;

    public ReporteMultitablaService(DataSource dataSource) {
        this.jdbc = new JdbcTemplate(dataSource);
    }

    public Resultado consultar(FiltrosReporte filtros, int limite) {
        ConsultaMultitabla.Consulta consulta = ConsultaMultitabla.construir(filtros, limite + 1);
        List<Fila> filas = jdbc.query(consulta.sql(), (rs, n) -> ConsultaMultitabla.mapear(rs),
                consulta.parametros().toArray());
        boolean truncado = filas.size() > limite;
        List<Fila> visibles = truncado ? new ArrayList<>(filas.subList(0, limite)) : filas;
        return new Resultado(visibles, truncado, ConsultaMultitabla.resumir(visibles));
    }

    public List<Opcion> categorias() {
        return opciones("SELECT id_categoria, nom_categoria FROM Categoria ORDER BY nom_categoria");
    }

    public List<Opcion> productos() {
        return opciones("SELECT id_menu, Productos FROM Menu ORDER BY Productos");
    }

    public List<Opcion> metodosPago() {
        return opciones("SELECT id_pago, Tipo_pago FROM Metodo_pago ORDER BY Tipo_pago");
    }

    private List<Opcion> opciones(String sql) {
        return jdbc.query(sql, (rs, n) -> new Opcion(rs.getInt(1), rs.getString(2)));
    }

    // ------------------------------------------------------------------ Excel

    public byte[] excel(Resultado resultado, FiltrosReporte filtros) {
        List<List<Object>> filas = new ArrayList<>();
        filas.add(List.of("Pedido", "Fecha", "Estado", "Prioridad", "Mesa", "Ubicación", "Cliente", "Mesero",
                "Categoría", "Producto", "Cantidad", "Precio unitario", "Subtotal", "Adiciones", "Factura",
                "Total factura", "Método de pago"));
        for (Fila f : resultado.filas()) {
            List<Object> fila = new ArrayList<>();
            fila.add(f.pedidoId()); fila.add(f.fecha()); fila.add(f.estado()); fila.add(f.prioridad());
            fila.add(f.mesa()); fila.add(f.ubicacionMesa()); fila.add(f.cliente()); fila.add(f.mesero());
            fila.add(f.categoria()); fila.add(f.producto()); fila.add(f.cantidad()); fila.add(f.precioUnitario());
            fila.add(f.subtotal()); fila.add(f.adiciones()); fila.add(f.facturaId()); fila.add(f.totalFactura());
            fila.add(f.metodoPago());
            filas.add(fila);
        }
        int[] anchos = {9, 17, 15, 11, 7, 15, 20, 18, 18, 28, 9, 15, 13, 32, 9, 14, 16};

        List<List<Object>> resumen = new ArrayList<>();
        resumen.add(List.of("Criterio", "Valor"));
        for (String[] par : criterios(filtros)) resumen.add(List.of(par[0], par[1]));
        resumen.add(List.of("", ""));
        Resumen r = resultado.resumen();
        resumen.add(List.of("Pedidos", r.pedidos()));
        resumen.add(List.of("Líneas de pedido", r.lineas()));
        resumen.add(List.of("Unidades vendidas", r.unidades()));
        resumen.add(List.of("Total de líneas", r.totalLineas()));
        resumen.add(List.of("Total facturado", r.totalFacturado()));
        resumen.add(List.of("Generado", LocalDateTime.now()));
        if (resultado.truncado()) resumen.add(List.of("Aviso", "Se exportaron solo las primeras " + MAX_EXPORTACION + " filas."));

        return XlsxWriter.escribir(List.of(
                new XlsxWriter.Hoja("Reporte multitabla", filas, anchos, true),
                new XlsxWriter.Hoja("Filtros y totales", resumen, new int[]{24, 40}, false)));
    }

    // -------------------------------------------------------------------- PDF

    public byte[] pdf(Resultado resultado, FiltrosReporte filtros) {
        try (ByteArrayOutputStream salida = new ByteArrayOutputStream()) {
            Document documento = new Document(PageSize.A4.rotate(), 24, 24, 28, 28);
            PdfWriter.getInstance(documento, salida);
            documento.open();
            try {
                documento.add(new Paragraph("SISPE - Reporte multitabla de pedidos", TITULO));
                StringBuilder criterios = new StringBuilder();
                for (String[] par : criterios(filtros)) {
                    if (criterios.length() > 0) criterios.append("   |   ");
                    criterios.append(par[0]).append(": ").append(par[1]);
                }
                documento.add(new Paragraph("Filtros - " + criterios, CELDA));
                Resumen r = resultado.resumen();
                documento.add(new Paragraph("Pedidos: " + r.pedidos() + "   |   Líneas: " + r.lineas()
                        + "   |   Unidades: " + r.unidades() + "   |   Total líneas: " + r.totalLineas()
                        + "   |   Total facturado: " + r.totalFacturado(), CELDA));
                documento.add(new Paragraph(" "));

                if (resultado.filas().isEmpty()) {
                    documento.add(new Paragraph("No hay resultados para los filtros aplicados.", CELDA));
                } else {
                    PdfPTable tabla = new PdfPTable(12);
                    tabla.setWidthPercentage(100);
                    tabla.setWidths(new float[]{5, 10, 8, 5, 11, 10, 15, 5, 8, 15, 6, 8});
                    tabla.setHeaderRows(1);
                    for (String c : new String[]{"Pedido", "Fecha", "Estado", "Mesa", "Cliente", "Categoría",
                            "Producto", "Cant.", "Subtotal", "Adiciones", "Factura", "Pago"}) {
                        PdfPCell celda = new PdfPCell(new Phrase(c, CABECERA));
                        celda.setHorizontalAlignment(Element.ALIGN_LEFT);
                        tabla.addCell(celda);
                    }
                    for (Fila f : resultado.filas()) {
                        celda(tabla, f.pedidoId()); celda(tabla, f.fecha() == null ? null : f.fecha().format(FECHA_HORA));
                        celda(tabla, f.estado()); celda(tabla, f.mesa()); celda(tabla, f.cliente());
                        celda(tabla, f.categoria()); celda(tabla, f.producto()); celda(tabla, f.cantidad());
                        celda(tabla, f.subtotal()); celda(tabla, f.adiciones()); celda(tabla, f.totalFactura());
                        celda(tabla, f.metodoPago());
                    }
                    documento.add(tabla);
                }
                if (resultado.truncado()) {
                    documento.add(new Paragraph("Se muestran solo las primeras " + MAX_EXPORTACION + " filas.", CELDA));
                }
            } finally {
                documento.close();
            }
            return salida.toByteArray();
        } catch (Exception e) {
            throw new IllegalStateException("No fue posible generar el PDF", e);
        }
    }

    private void celda(PdfPTable tabla, Object valor) {
        tabla.addCell(new PdfPCell(new Phrase(valor == null ? "" : valor.toString(), CELDA)));
    }

    /** Filtros aplicados en texto, para encabezar el PDF y la hoja de resumen del Excel. */
    private List<String[]> criterios(FiltrosReporte f) {
        List<String[]> lista = new ArrayList<>();
        lista.add(new String[]{"Desde", f.getDesde() == null ? "sin límite" : f.getDesde().toString()});
        lista.add(new String[]{"Hasta", f.getHasta() == null ? "sin límite" : f.getHasta().toString()});
        lista.add(new String[]{"Estado", vacio(f.getEstado()) ? "todos" : f.getEstado()});
        lista.add(new String[]{"Prioridad", vacio(f.getPrioridad()) ? "todas" : f.getPrioridad()});
        lista.add(new String[]{"Mesa", f.getMesa() == null ? "todas" : f.getMesa().toString()});
        lista.add(new String[]{"Categoría", f.getCategoria() == null ? "todas" : nombre(categorias(), f.getCategoria())});
        lista.add(new String[]{"Producto", f.getProducto() == null ? "todos" : nombre(productos(), f.getProducto())});
        lista.add(new String[]{"Método de pago", f.getMetodoPago() == null ? "todos" : nombre(metodosPago(), f.getMetodoPago())});
        return lista;
    }

    private static boolean vacio(String texto) {
        return texto == null || texto.isBlank();
    }

    private static String nombre(List<Opcion> opciones, Integer id) {
        return opciones.stream().filter(o -> o.id().equals(id)).map(Opcion::nombre).findFirst().orElse("#" + id);
    }
}
