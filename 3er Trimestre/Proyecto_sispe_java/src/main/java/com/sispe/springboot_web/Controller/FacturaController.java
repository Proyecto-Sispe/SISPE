package com.sispe.springboot_web.Controller;

import com.sispe.springboot_web.Model.Factura;
import com.sispe.springboot_web.Model.Pedido;
import com.sispe.springboot_web.Model.SesionMesa;
import com.sispe.springboot_web.Repository.DetallePedidoAdicionRepository;
import com.sispe.springboot_web.Repository.DetallePedidoRepository;
import com.sispe.springboot_web.Repository.FacturaMetodoPagoRepository;
import com.sispe.springboot_web.Repository.FacturaRepository;
import com.sispe.springboot_web.Repository.PedidoRepository;
import com.sispe.springboot_web.Repository.SesionMesaRepository;
import com.sispe.springboot_web.Service.FacturaPdfService;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;

@Controller
@RequestMapping("/facturas")
public class FacturaController {
    private final FacturaRepository facturas;
    private final PedidoRepository pedidos;
    private final SesionMesaRepository sesiones;
    private final DetallePedidoRepository detalles;
    private final DetallePedidoAdicionRepository detalleAdiciones;
    private final FacturaMetodoPagoRepository facturaMetodoPagos;
    private final FacturaPdfService pdfService;

    public FacturaController(FacturaRepository facturas, PedidoRepository pedidos, SesionMesaRepository sesiones,
                              DetallePedidoRepository detalles, DetallePedidoAdicionRepository detalleAdiciones,
                              FacturaMetodoPagoRepository facturaMetodoPagos, FacturaPdfService pdfService) {
        this.facturas = facturas;
        this.pedidos = pedidos;
        this.sesiones = sesiones;
        this.detalles = detalles;
        this.detalleAdiciones = detalleAdiciones;
        this.facturaMetodoPagos = facturaMetodoPagos;
        this.pdfService = pdfService;
    }

    /** Fila enriquecida para que el admin vea todo de un vistazo en /facturas */
    public record FilaFactura(Long facturaId, Long pedidoId, Long mesaId, String cliente,
                               String fecha, String total, boolean pagada, String metodoPago) {}

    @GetMapping
    public String index(Model model) {
        List<Factura> todas = facturas.findAll();
        List<FilaFactura> filas = new ArrayList<>();

        for (Factura f : todas) {
            Pedido pedido = pedidos.findById(f.getPedidoId()).orElse(null);
            Long mesaId = pedido != null ? pedido.getMesaId() : null;
            boolean pagada = pedido != null && Boolean.TRUE.equals(pedido.getConfirmado());

            String cliente = "—";
            if (pedido != null && pedido.getSesionQrId() != null) {
                SesionMesa sesion = sesiones.findById(pedido.getSesionQrId()).orElse(null);
                if (sesion != null) cliente = sesion.getNombreCliente();
            }

            String metodoPago = facturaMetodoPagos.findByFactura_Id(f.getId())
                    .map(pago -> pago.getMetodoPago().getTipo())
                    .orElse("—");

            filas.add(new FilaFactura(
                    f.getId(), f.getPedidoId(), mesaId, cliente,
                    f.getFechaHora() != null ? f.getFechaHora().toString() : "—",
                    f.getTotal() != null ? f.getTotal().toString() : "0",
                    pagada, metodoPago
            ));
        }

        model.addAttribute("filas", filas);
        return "facturas/index";
    }

    @GetMapping("/{id}")
    public String ver(@PathVariable Long id, Model model) {
        Factura factura = facturas.findById(id).orElseThrow();
        Pedido pedido = pedidos.findById(factura.getPedidoId()).orElseThrow();
        SesionMesa sesion = pedido.getSesionQrId() == null ? null : sesiones.findById(pedido.getSesionQrId()).orElse(null);

        model.addAttribute("factura", factura);
        model.addAttribute("pedido", pedido);
        model.addAttribute("sesion", sesion);
        model.addAttribute("items", detalles.findByPedidoId(pedido.getId()));
        model.addAttribute("adicionesRepo", detalleAdiciones);
        model.addAttribute("pago", facturaMetodoPagos.findByFactura_Id(id).orElse(null));
        return "facturas/ver";
    }

    @GetMapping("/{id}/pdf")
    public ResponseEntity<byte[]> descargarPdf(@PathVariable Long id) {
        byte[] pdf = pdfService.generar(id);
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=factura-" + id + ".pdf")
                .contentType(MediaType.APPLICATION_PDF)
                .body(pdf);
    }
}