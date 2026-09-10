package com.sispe.springboot_web.Service;

import java.io.ByteArrayOutputStream;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.springframework.stereotype.Service;

import com.lowagie.text.Document;
import com.lowagie.text.Element;
import com.lowagie.text.Font;
import com.lowagie.text.FontFactory;
import com.lowagie.text.Paragraph;
import com.lowagie.text.Phrase;
import com.lowagie.text.pdf.PdfPCell;
import com.lowagie.text.pdf.PdfPTable;
import com.lowagie.text.pdf.PdfWriter;
import com.sispe.springboot_web.Model.DetallePedido;
import com.sispe.springboot_web.Model.Factura;
import com.sispe.springboot_web.Model.Insumo;
import com.sispe.springboot_web.Model.Pedido;
import com.sispe.springboot_web.Repository.DetallePedidoRepository;
import com.sispe.springboot_web.Repository.FacturaRepository;
import com.sispe.springboot_web.Repository.InsumoRepository;
import com.sispe.springboot_web.Repository.PedidoRepository;

@Service
public class ReporteService {

    private static final Font TITULO = FontFactory.getFont(FontFactory.HELVETICA_BOLD, 16);
    private static final Font SUBTITULO = FontFactory.getFont(FontFactory.HELVETICA_BOLD, 12);
    private static final Font CABECERA = FontFactory.getFont(FontFactory.HELVETICA_BOLD, 9);
    private static final Font CELDA = FontFactory.getFont(FontFactory.HELVETICA, 9);

    private final PedidoRepository pedidos;
    private final FacturaRepository facturas;
    private final InsumoRepository insumos;
    private final DetallePedidoRepository detalles;

    public ReporteService(PedidoRepository p, FacturaRepository f, InsumoRepository i, DetallePedidoRepository d) {
        pedidos = p; facturas = f; insumos = i; detalles = d;
    }

    /**
     * Reúne los datos del reporte aplicando los filtros una sola vez. Las facturas y
     * los detalles se acotan a los pedidos que superaron el filtro, para que todos los
     * totales de la pantalla hablen del mismo conjunto.
     */
    public Map<String,Object> datos(LocalDate desde, LocalDate hasta, String estado) {
        List<Pedido> filtrados = pedidos.findAll().stream().filter(p -> dentroDelRango(p, desde, hasta) && coincideEstado(p, estado)).toList();
        Set<Long> ids = new java.util.HashSet<>();
        for (Pedido pedido : filtrados) {
            if (pedido.getId() != null) {
                ids.add(pedido.getId());
            }
        }

        List<Factura> facturasFiltradas = facturas.findAll().stream().filter(f -> ids.contains(f.getPedidoId())).toList();
        List<DetallePedido> detallesFiltrados = detalles.findAll().stream().filter(d -> ids.contains(d.getPedidoId())).toList();
        BigDecimal totalVentas = BigDecimal.ZERO;
        for (Factura factura : facturasFiltradas) {
            BigDecimal total = factura.getTotal();
            totalVentas = totalVentas.add(total == null ? BigDecimal.ZERO : total);
        }

        Map<String,Object> datos = new LinkedHashMap<>();
        datos.put("pedidos", filtrados);
        datos.put("facturas", facturasFiltradas);
        datos.put("detalles", detallesFiltrados);
        datos.put("insumos", insumos.findAll());
        datos.put("totalPedidos", filtrados.size());
        datos.put("totalVentas", totalVentas);
        return datos;
    }

    private boolean dentroDelRango(Pedido pedido, LocalDate desde, LocalDate hasta) {
        if (pedido.getFechaPedido() == null) return true;
        LocalDate fecha = pedido.getFechaPedido().toLocalDate();
        return (desde == null || !fecha.isBefore(desde)) && (hasta == null || !fecha.isAfter(hasta));
    }

    private boolean coincideEstado(Pedido pedido, String estado) {
        return estado == null || estado.isBlank() || estado.equalsIgnoreCase(pedido.getEstado());
    }

    /**
     * Genera el PDF correspondiente al tipo solicitado. Cada tipo imprime una sección
     * distinta sobre el mismo conjunto de datos ya filtrado.
     */
    public byte[] pdf(String tipo, Map<String,Object> datos) {
        // El documento, sus párrafos y el buffer son objetos del heap; las referencias locales
        // viven en el stack durante esta llamada y el recolector recupera el heap al terminar.
        try (ByteArrayOutputStream salida = new ByteArrayOutputStream()) {
            Document documento = new Document();
            PdfWriter.getInstance(documento, salida);
            documento.open();
            try {
                documento.add(new Paragraph("SISPE - Reporte " + tipo, TITULO));
                documento.add(new Paragraph("Pedidos: " + datos.get("totalPedidos") + "   |   Ventas: " + datos.get("totalVentas"), CELDA));
                documento.add(new Paragraph(" "));
                switch (tipo == null ? "" : tipo.toLowerCase()) {
                    case "producto" -> seccionProducto(documento, datos);
                    case "usuarios" -> seccionUsuarios(documento, datos);
                    case "ventas" -> seccionVentas(documento, datos);
                    case "inventario" -> seccionInventario(documento, datos);
                    default -> seccionGeneral(documento, datos);
                }
            } finally {
                documento.close();
            }
            return salida.toByteArray();
        } catch (Exception e) {
            throw new IllegalStateException("No fue posible generar el PDF", e);
        }
    }

    private void seccionGeneral(Document documento, Map<String,Object> datos) {
        documento.add(new Paragraph("Pedidos del periodo", SUBTITULO));
        PdfPTable tabla = tabla("ID", "Mesa", "Estado", "Prioridad", "Fecha");
        for (Pedido p : pedidos(datos)) {
            fila(tabla, p.getId(), p.getMesaId(), p.getEstado(), p.getPrioridad(), p.getFechaPedido());
        }
        agregar(documento, tabla, pedidos(datos).isEmpty());
    }

    private void seccionProducto(Document documento, Map<String,Object> datos) {
        documento.add(new Paragraph("Ventas por producto", SUBTITULO));
        Map<String,int[]> unidades = new LinkedHashMap<>();
        Map<String,BigDecimal> importes = new LinkedHashMap<>();
        for (DetallePedido d : detalles(datos)) {
            String producto = d.getMenu() == null ? "(sin producto)" : d.getMenu().getProducto();
            Integer cantidadRegistrada = d.getCantidad();
            Integer cantidad = cantidadRegistrada;
            if (cantidad == null) {
                cantidad = Integer.valueOf(0);
            }
            unidades.computeIfAbsent(producto, k -> new int[1])[0] += cantidad.intValue();
            BigDecimal importe = d.getValorVenta() == null ? BigDecimal.ZERO : d.getValorVenta().multiply(BigDecimal.valueOf(cantidad.longValue()));
            importes.put(producto, importes.getOrDefault(producto, BigDecimal.ZERO).add(importe));
        }
        PdfPTable tabla = tabla("Producto", "Unidades", "Importe");
        unidades.forEach((producto, cantidad) -> fila(tabla, producto, cantidad[0], importes.get(producto)));
        agregar(documento, tabla, unidades.isEmpty());
    }

    private void seccionUsuarios(Document documento, Map<String,Object> datos) {
        documento.add(new Paragraph("Pedidos atendidos por mesero", SUBTITULO));
        Map<Object,int[]> porMesero = new LinkedHashMap<>();
        for (Pedido p : pedidos(datos)) {
            Object mesero = p.getMeseroId() == null ? "(sin asignar)" : p.getMeseroId();
            porMesero.computeIfAbsent(mesero, k -> new int[1])[0]++;
        }
        PdfPTable tabla = tabla("Mesero", "Pedidos");
        porMesero.forEach((mesero, cantidad) -> fila(tabla, mesero, cantidad[0]));
        agregar(documento, tabla, porMesero.isEmpty());
    }

    private void seccionVentas(Document documento, Map<String,Object> datos) {
        documento.add(new Paragraph("Facturas del periodo", SUBTITULO));
        @SuppressWarnings("unchecked")
        List<Factura> lista = (List<Factura>) datos.getOrDefault("facturas", List.of());
        PdfPTable tabla = tabla("Factura", "Pedido", "Fecha", "Total");
        for (Factura f : lista) {
            fila(tabla, f.getId(), f.getPedidoId(), f.getFechaHora(), f.getTotal());
        }
        agregar(documento, tabla, lista.isEmpty());
    }

    private void seccionInventario(Document documento, Map<String,Object> datos) {
        documento.add(new Paragraph("Stock de insumos", SUBTITULO));
        @SuppressWarnings("unchecked")
        List<Insumo> lista = (List<Insumo>) datos.getOrDefault("insumos", List.of());
        PdfPTable tabla = tabla("Insumo", "Stock", "Mínimo", "Unidad", "Situación");
        for (Insumo i : lista) {
            boolean bajo = i.getStockActual() != null && i.getStockMinimo() != null && i.getStockActual().compareTo(i.getStockMinimo()) < 0;
            fila(tabla, i.getNombre(), i.getStockActual(), i.getStockMinimo(), i.getUnidad(), bajo ? "BAJO MÍNIMO" : "OK");
        }
        agregar(documento, tabla, lista.isEmpty());
    }

    @SuppressWarnings("unchecked")
    private List<Pedido> pedidos(Map<String,Object> datos) {
        return (List<Pedido>) datos.getOrDefault("pedidos", List.of());
    }

    @SuppressWarnings("unchecked")
    private List<DetallePedido> detalles(Map<String,Object> datos) {
        return (List<DetallePedido>) datos.getOrDefault("detalles", List.of());
    }

    private PdfPTable tabla(String... cabeceras) {
        PdfPTable tabla = new PdfPTable(cabeceras.length);
        tabla.setWidthPercentage(100);
        tabla.setSpacingBefore(8f);
        for (String cabecera : cabeceras) {
            PdfPCell celda = new PdfPCell(new Phrase(cabecera, CABECERA));
            celda.setHorizontalAlignment(Element.ALIGN_LEFT);
            tabla.addCell(celda);
        }
        return tabla;
    }

    private void fila(PdfPTable tabla, Object... valores) {
        List<String> textos = new ArrayList<>(valores.length);
        for (Object valor : valores) {
            textos.add(valor == null ? "" : valor.toString());
        }
        textos.forEach(texto -> tabla.addCell(new PdfPCell(new Phrase(texto, CELDA))));
    }

    private void agregar(Document documento, PdfPTable tabla, boolean vacia) {
        if (vacia) {
            documento.add(new Paragraph("No hay resultados para los filtros aplicados.", CELDA));
            return;
        }
        documento.add(tabla);
    }
}
