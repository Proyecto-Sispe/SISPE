package com.sispe.springboot_web.Service;

import com.lowagie.text.*;
import com.lowagie.text.pdf.PdfPCell;
import com.lowagie.text.pdf.PdfPTable;
import com.lowagie.text.pdf.PdfWriter;
import com.sispe.springboot_web.Model.*;
import com.sispe.springboot_web.Repository.*;
import org.springframework.stereotype.Service;

import java.awt.Color;
import java.io.ByteArrayOutputStream;
import java.math.BigDecimal;
import java.time.format.DateTimeFormatter;
import java.util.List;

@Service
public class FacturaPdfService {

    private static final Font TITULO = FontFactory.getFont(FontFactory.HELVETICA_BOLD, 18);
    private static final Font SUBTITULO = FontFactory.getFont(FontFactory.HELVETICA, 11, Font.ITALIC);
    private static final Font ETIQUETA = FontFactory.getFont(FontFactory.HELVETICA_BOLD, 10);
    private static final Font TEXTO = FontFactory.getFont(FontFactory.HELVETICA, 10);
    private static final Font CABECERA = FontFactory.getFont(FontFactory.HELVETICA_BOLD, 9, Color.WHITE);
    private static final Font TOTAL = FontFactory.getFont(FontFactory.HELVETICA_BOLD, 14);
    private static final DateTimeFormatter FECHA = DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm");

    private final FacturaRepository facturas;
    private final PedidoRepository pedidos;
    private final SesionMesaRepository sesiones;
    private final DetallePedidoRepository detalles;
    private final DetallePedidoAdicionRepository detalleAdiciones;
    private final FacturaMetodoPagoRepository facturaMetodoPagos;

    public FacturaPdfService(FacturaRepository facturas, PedidoRepository pedidos, SesionMesaRepository sesiones,
                              DetallePedidoRepository detalles, DetallePedidoAdicionRepository detalleAdiciones,
                              FacturaMetodoPagoRepository facturaMetodoPagos) {
        this.facturas = facturas;
        this.pedidos = pedidos;
        this.sesiones = sesiones;
        this.detalles = detalles;
        this.detalleAdiciones = detalleAdiciones;
        this.facturaMetodoPagos = facturaMetodoPagos;
    }

    public byte[] generar(Long facturaId) {
        Factura factura = facturas.findById(facturaId).orElseThrow();
        Pedido pedido = pedidos.findById(factura.getPedidoId()).orElseThrow();
        SesionMesa sesion = pedido.getSesionQrId() == null ? null : sesiones.findById(pedido.getSesionQrId()).orElse(null);
        List<DetallePedido> items = detalles.findByPedidoId(pedido.getId());
        FacturaMetodoPago pago = facturaMetodoPagos.findByFactura_Id(facturaId).orElse(null);

        try (ByteArrayOutputStream salida = new ByteArrayOutputStream()) {
            Document documento = new Document(PageSize.A5);
            PdfWriter.getInstance(documento, salida);
            documento.open();

            documento.add(new Paragraph("SISPE", TITULO));
            documento.add(new Paragraph("Factura de venta", SUBTITULO));
            documento.add(new Paragraph(" "));

            PdfPTable meta = new PdfPTable(2);
            meta.setWidthPercentage(100);
            agregarMeta(meta, "Factura N°", "#" + factura.getId());
            agregarMeta(meta, "Fecha", factura.getFechaHora() != null ? factura.getFechaHora().format(FECHA) : "-");
            agregarMeta(meta, "Mesa", String.valueOf(pedido.getMesaId()));
            if (sesion != null) {
                agregarMeta(meta, "Cliente", sesion.getNombreCliente());
                agregarMeta(meta, "Cédula", String.valueOf(sesion.getCedulaCliente()));
            }
            documento.add(meta);
            documento.add(new Paragraph(" "));

            PdfPTable tabla = new PdfPTable(new float[]{4, 1, 2, 2});
            tabla.setWidthPercentage(100);
            celdaCabecera(tabla, "Producto");
            celdaCabecera(tabla, "Cant.");
            celdaCabecera(tabla, "Precio unit.");
            celdaCabecera(tabla, "Subtotal");

            BigDecimal totalCalculado = BigDecimal.ZERO;
            for (DetallePedido item : items) {
                StringBuilder nombre = new StringBuilder(item.getMenu().getProducto());
                for (DetallePedidoAdicion extra : detalleAdiciones.findByDetallePedido_Id(item.getId())) {
                    nombre.append("\n+ ").append(extra.getAdicion().getNombre());
                }
                if (item.getObservaciones() != null && !item.getObservaciones().isBlank()) {
                    nombre.append("\nNota: ").append(item.getObservaciones());
                }
                BigDecimal subtotal = item.getValorVenta().multiply(BigDecimal.valueOf(item.getCantidad()));
                for (DetallePedidoAdicion extra : detalleAdiciones.findByDetallePedido_Id(item.getId())) {
                    subtotal = subtotal.add(extra.getAdicion().getPrecio().multiply(BigDecimal.valueOf(extra.getCantidad())));
                }
                totalCalculado = totalCalculado.add(subtotal);

                tabla.addCell(new PdfPCell(new Phrase(nombre.toString(), TEXTO)));
                tabla.addCell(celdaTexto(String.valueOf(item.getCantidad())));
                tabla.addCell(celdaTexto(formatoMoneda(item.getValorVenta())));
                tabla.addCell(celdaTexto(formatoMoneda(subtotal)));
            }
            documento.add(tabla);
            documento.add(new Paragraph(" "));

            if (pago != null) {
                Paragraph metodo = new Paragraph("Método de pago: " + pago.getMetodoPago().getTipo(), ETIQUETA);
                documento.add(metodo);
            }

            BigDecimal totalFinal = factura.getTotal() != null ? factura.getTotal() : totalCalculado;
            Paragraph total = new Paragraph("TOTAL: " + formatoMoneda(totalFinal) + " $", TOTAL);
            total.setSpacingBefore(10f);
            documento.add(total);

            documento.close();
            return salida.toByteArray();
        } catch (Exception ex) {
            throw new IllegalStateException("No fue posible generar el PDF de la factura", ex);
        }
    }

    private void agregarMeta(PdfPTable tabla, String etiqueta, String valor) {
        PdfPCell celdaEtiqueta = new PdfPCell(new Phrase(etiqueta, ETIQUETA));
        celdaEtiqueta.setBorder(Rectangle.NO_BORDER);
        PdfPCell celdaValor = new PdfPCell(new Phrase(valor, TEXTO));
        celdaValor.setBorder(Rectangle.NO_BORDER);
        tabla.addCell(celdaEtiqueta);
        tabla.addCell(celdaValor);
    }

    private void celdaCabecera(PdfPTable tabla, String texto) {
        PdfPCell celda = new PdfPCell(new Phrase(texto, CABECERA));
        celda.setBackgroundColor(new Color(31, 36, 45)); // var(--navy)
        celda.setPadding(6f);
        tabla.addCell(celda);
    }

    private PdfPCell celdaTexto(String texto) {
        PdfPCell celda = new PdfPCell(new Phrase(texto, TEXTO));
        celda.setPadding(5f);
        return celda;
    }

    private String formatoMoneda(BigDecimal valor) {
        return String.format("%,.0f", valor == null ? BigDecimal.ZERO : valor);
    }
}