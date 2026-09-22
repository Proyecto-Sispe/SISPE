// Controller/CocinaController.java
package com.sispe.springboot_web.Controller;

import com.sispe.springboot_web.Model.DetallePedido;
import com.sispe.springboot_web.Model.DetallePedidoAdicion;
import com.sispe.springboot_web.Model.Pedido;
import com.sispe.springboot_web.Repository.DetallePedidoAdicionRepository;
import com.sispe.springboot_web.Repository.DetallePedidoRepository;
import com.sispe.springboot_web.Repository.PedidoRepository;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Controller
@RequestMapping("/cocina")
public class CocinaController {
    /** Línea de un pedido tal como la ve cocina: producto, cantidad, nota del cliente y adiciones. */
    public record LineaPedido(String producto, int cantidad, String nota, List<String> adiciones) { }

    private final PedidoRepository pedidos;
    private final com.sispe.springboot_web.Service.PedidoService pedidoService;
    private final DetallePedidoRepository detalles;
    private final DetallePedidoAdicionRepository detalleAdiciones;

    public CocinaController(PedidoRepository pedidos, com.sispe.springboot_web.Service.PedidoService pedidoService,
                            DetallePedidoRepository detalles, DetallePedidoAdicionRepository detalleAdiciones) {
        this.pedidos = pedidos;
        this.pedidoService = pedidoService;
        this.detalles = detalles;
        this.detalleAdiciones = detalleAdiciones;
    }

    @GetMapping
    public String index(Model model) {
        List<Pedido> activos = pedidos.findByEstadoInOrderByFechaPedidoAsc(
                List.of("pendiente", "en_preparacion", "en_camino"));
        Map<Long, List<LineaPedido>> productosPorPedido = new HashMap<>();
        for (Pedido pedido : activos) {
            productosPorPedido.put(pedido.getId(), lineasDe(pedido.getId()));
        }
        model.addAttribute("pedidos", activos);
        model.addAttribute("productosPorPedido", productosPorPedido);
        return "cocina/index";
    }

    private List<LineaPedido> lineasDe(Long pedidoId) {
        return detalles.findByPedidoId(pedidoId).stream().map(this::aLinea).toList();
    }

    private LineaPedido aLinea(DetallePedido detalle) {
        List<String> adiciones = detalleAdiciones.findByDetallePedido_Id(detalle.getId()).stream()
                .map(this::textoAdicion).toList();
        String producto = detalle.getMenu() == null ? "(producto eliminado)" : detalle.getMenu().getProducto();
        int cantidad = detalle.getCantidad() == null ? 0 : detalle.getCantidad();
        String nota = detalle.getObservaciones() == null || detalle.getObservaciones().isBlank() ? null : detalle.getObservaciones();
        return new LineaPedido(producto, cantidad, nota, adiciones);
    }

    private String textoAdicion(DetallePedidoAdicion extra) {
        return extra.getCantidad() + "x " + extra.getAdicion().getNombre();
    }

    @PostMapping("/pedido/{id}/estado")
    public String cambiarEstado(@PathVariable Long id, @RequestParam String estado, RedirectAttributes attrs) {
        try {
            pedidoService.cambiarEstado(id, estado);
            attrs.addFlashAttribute("ok", "Pedido #" + id + " actualizado.");
        } catch (IllegalStateException | IllegalArgumentException ex) {
            attrs.addFlashAttribute("error", ex.getMessage());
        }
        return "redirect:/cocina";
    }
}