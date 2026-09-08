package com.sispe.springboot_web.Controller;

import com.sispe.springboot_web.Model.DetallePedido;
import com.sispe.springboot_web.Model.Menu;
import com.sispe.springboot_web.Model.Mesa;
import com.sispe.springboot_web.Repository.DetallePedidoRepository;
import com.sispe.springboot_web.Repository.MenuRepository;
import com.sispe.springboot_web.Repository.MesaRepository;
import com.sispe.springboot_web.Service.SesionMesaService;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.dao.DataAccessException;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.util.List;

@Controller
@RequiredArgsConstructor
@RequestMapping("/cliente")
public class ClienteController {
    private final MenuRepository menuRepository;
    private final MesaRepository mesaRepository;
    private final DetallePedidoRepository detalleRepository;
    private final SesionMesaService sesionMesaService;

    @GetMapping("/escanear/{idMesa}")
    public String formularioEscaneo(@PathVariable Integer idMesa, Model model) {
        Mesa mesa = mesaRepository.findById(idMesa).orElseThrow();
        model.addAttribute("mesa", mesa);
        return "cliente/escanear";
    }

    @PostMapping("/escanear/{idMesa}")
    public String registrarEnMesa(@PathVariable Integer idMesa, @RequestParam String nombre,
                                   @RequestParam Integer cedula, HttpSession session,
                                   RedirectAttributes attrs) {
        try {
            Long idPedido = sesionMesaService.registrarClienteYCrearPedido(idMesa, nombre, cedula);
            session.setAttribute("pedidoActivoId", idPedido);
            session.setAttribute("mesaActivaId", idMesa);
            return "redirect:/menu/digital";
        } catch (DataAccessException ex) {
            attrs.addFlashAttribute("error", "Esta mesa ya está ocupada. Avisa a un mesero.");
            return "redirect:/cliente/escanear/" + idMesa;
        }
    }

    @PostMapping("/carrito/agregar")
    public String agregar(@RequestParam Integer productoId, HttpSession session, RedirectAttributes attrs) {
        Long idPedido = (Long) session.getAttribute("pedidoActivoId");
        if (idPedido == null) {
            attrs.addFlashAttribute("error", "Escanea el código QR de tu mesa antes de pedir.");
            return "redirect:/menu/digital";
        }
        Menu producto = menuRepository.findById(productoId).orElseThrow();
        DetallePedido detalle = DetallePedido.builder()
                .pedidoId(idPedido)
                .menu(producto)
                .cantidad(1)
                .valorVenta(producto.getPrecio())
                .build();
        detalleRepository.save(detalle);
        return "redirect:/menu/digital";
    }

    @GetMapping("/pedido")
    public String pedido(HttpSession session, Model model) {
        Long idPedido = (Long) session.getAttribute("pedidoActivoId");
        List<DetallePedido> items = idPedido == null ? List.of() : detalleRepository.findByPedidoId(idPedido);
        model.addAttribute("items", items);
        return "cliente/pedido";
    }

    @PostMapping("/carrito/vaciar")
    public String vaciar(HttpSession session) {
        Long idPedido = (Long) session.getAttribute("pedidoActivoId");
        if (idPedido != null) detalleRepository.deleteByPedidoId(idPedido);
        return "redirect:/cliente/pedido";
    }
}