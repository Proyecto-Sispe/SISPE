package com.sispe.springboot_web.Service;

import com.lowagie.text.*;
import com.lowagie.text.pdf.PdfWriter;
import com.sispe.springboot_web.Model.*;
import com.sispe.springboot_web.Repository.*;
import org.springframework.stereotype.Service;
import java.io.ByteArrayOutputStream;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.*;

@Service
public class ReporteService {
    private final PedidoRepository pedidos; private final FacturaRepository facturas; private final InsumoRepository insumos;
    public ReporteService(PedidoRepository p, FacturaRepository f, InsumoRepository i) { pedidos=p; facturas=f; insumos=i; }
    public Map<String,Object> datos(LocalDate desde, LocalDate hasta, String tipo, String estado) {
        List<Pedido> filtrados = pedidos.findAll().stream().filter(p -> (desde == null || p.getFechaPedido() == null || !p.getFechaPedido().toLocalDate().isBefore(desde)) && (hasta == null || p.getFechaPedido() == null || !p.getFechaPedido().toLocalDate().isAfter(hasta)) && (estado == null || estado.isBlank() || estado.equalsIgnoreCase(p.getEstado()))).toList();
        Map<String,Object> datos = new LinkedHashMap<>(); datos.put("pedidos", filtrados); datos.put("facturas", facturas.findAll()); datos.put("insumos", insumos.findAll()); datos.put("totalPedidos", filtrados.size());
        datos.put("totalVentas", facturas.findAll().stream().map(f -> f.getTotal() == null ? BigDecimal.ZERO : f.getTotal()).reduce(BigDecimal.ZERO, BigDecimal::add)); return datos;
    }
    public byte[] pdf(String titulo, Map<String,Object> datos) {
        // El documento, sus párrafos y el buffer son objetos del heap; las referencias locales
        // viven en el stack durante esta llamada y el recolector recupera el heap al terminar.
        try (ByteArrayOutputStream salida = new ByteArrayOutputStream()) {
            Document documento = new Document(); PdfWriter.getInstance(documento, salida); documento.open();
            documento.add(new Paragraph("SISPE - " + titulo)); documento.add(new Paragraph("Pedidos: " + datos.get("totalPedidos"))); documento.add(new Paragraph("Ventas: " + datos.get("totalVentas"))); documento.add(new Paragraph("Insumos registrados: " + ((List<?>) datos.get("insumos")).size())); documento.close(); return salida.toByteArray();
        } catch (Exception e) { throw new IllegalStateException("No fue posible generar el PDF", e); }
    }
}
