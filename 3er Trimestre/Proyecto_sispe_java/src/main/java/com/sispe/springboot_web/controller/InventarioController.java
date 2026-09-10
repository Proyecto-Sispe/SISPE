package com.sispe.springboot_web.controller;

import com.sispe.springboot_web.model.*;
import com.sispe.springboot_web.repository.MenuRepository;
import com.sispe.springboot_web.service.InventarioService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;
import java.math.BigDecimal;

@Controller
@RequestMapping("/admin/inventario")
@PreAuthorize("hasRole('ADMINISTRADOR')")
public class InventarioController {
    private final InventarioService service;
    private final MenuRepository menus;
    public InventarioController(InventarioService service, MenuRepository menus) { this.service = service; this.menus = menus; }

    @GetMapping public String index(Model model) {
        model.addAttribute("insumos", service.listar());
        model.addAttribute("recetas", service.recetas());
        model.addAttribute("menus", menus.findAll());
        return "admin/inventario";
    }
    @PostMapping("/insumos") public String guardarInsumo(@RequestParam String nombre, @RequestParam BigDecimal stockActual,
            @RequestParam BigDecimal stockMinimo, @RequestParam String unidad) {
        service.guardar(Insumo.builder().nombre(nombre).stockActual(stockActual).stockMinimo(stockMinimo).unidad(unidad).activo(true).build());
        return "redirect:/admin/inventario?guardado";
    }
    @PostMapping("/recetas") public String guardarReceta(@RequestParam Integer menuId, @RequestParam Long insumoId, @RequestParam BigDecimal cantidad) {
        Insumo insumo = service.buscar(insumoId);
        Menu menu = menus.findById(menuId).orElseThrow(() -> new IllegalArgumentException("Producto no encontrado: " + menuId));
        service.guardarReceta(MenuInsumo.builder().menu(menu).insumo(insumo).cantidad(cantidad).build());
        return "redirect:/admin/inventario?receta";
    }
}