package com.login.demo.controller;

import com.login.demo.repository.MenuRepository;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import java.util.ArrayList;
import java.util.List;

@Controller
@RequiredArgsConstructor
@RequestMapping("/cliente")
public class ClienteController {
    private final MenuRepository menuRepository;

    @PostMapping("/carrito/agregar")
    public String agregar(@RequestParam Integer productoId, HttpSession session) {
        List<Integer> carrito = obtenerCarrito(session);
        carrito.add(productoId);
        session.setAttribute("carrito", carrito);
        return "redirect:/menu/digital";
    }

    @GetMapping("/pedido")
    public String pedido(HttpSession session, Model model) {
        List<Integer> ids = obtenerCarrito(session);
        model.addAttribute("productos", ids.stream().map(menuRepository::findById).flatMap(java.util.Optional::stream).toList());
        return "cliente/pedido";
    }

    @PostMapping("/carrito/vaciar")
    public String vaciar(HttpSession session) { session.removeAttribute("carrito"); return "redirect:/cliente/pedido"; }

    @SuppressWarnings("unchecked")
    private List<Integer> obtenerCarrito(HttpSession session) {
        Object actual = session.getAttribute("carrito");
        if (actual instanceof List<?>) return (List<Integer>) actual;
        List<Integer> nuevo = new ArrayList<>(); session.setAttribute("carrito", nuevo); return nuevo;
    }
}
