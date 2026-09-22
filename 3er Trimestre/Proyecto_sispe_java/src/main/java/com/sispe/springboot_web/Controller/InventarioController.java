package com.sispe.springboot_web.Controller;

import com.sispe.springboot_web.Model.*;
import com.sispe.springboot_web.Repository.MenuRepository;
import com.sispe.springboot_web.Service.InventarioService;
import org.springframework.dao.DataAccessException;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;
import org.springframework.security.access.prepost.PreAuthorize;
import java.math.BigDecimal;

@Controller
@RequestMapping("/admin/inventario")
@PreAuthorize("hasRole('ADMINISTRADOR')")
public class InventarioController {
    private static final String REDIRECT_INVENTARIO = "redirect:/admin/inventario";
    private static final String ATTR_OK = "ok";
    private static final String ATTR_ERROR = "error";
    /** Límite de la columna DECIMAL(12,3) de la base de datos. */
    private static final BigDecimal MAXIMO = new BigDecimal("999999999.999");

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
            @RequestParam BigDecimal stockMinimo, @RequestParam String unidad, RedirectAttributes attrs) {
        if (nombre.isBlank() || unidad.isBlank()) return error(attrs, "El nombre y la unidad del insumo son obligatorios.");
        String problema = validarStocks(stockActual, stockMinimo);
        if (problema != null) return error(attrs, problema);
        try {
            service.guardar(Insumo.builder().nombre(nombre.trim()).stockActual(stockActual).stockMinimo(stockMinimo).unidad(unidad.trim()).activo(true).build());
            attrs.addFlashAttribute(ATTR_OK, "Insumo «" + nombre.trim() + "» guardado correctamente.");
        } catch (DataAccessException ex) {
            attrs.addFlashAttribute(ATTR_ERROR, "No se pudo guardar el insumo. Es posible que ya exista uno con el nombre «" + nombre.trim() + "».");
        }
        return REDIRECT_INVENTARIO;
    }

    @PostMapping("/insumos/{id}/actualizar") public String actualizarInsumo(@PathVariable Long id, @RequestParam BigDecimal stockActual,
            @RequestParam BigDecimal stockMinimo, RedirectAttributes attrs) {
        String problema = validarStocks(stockActual, stockMinimo);
        if (problema != null) return error(attrs, problema);
        try {
            Insumo insumo = service.actualizar(id, stockActual, stockMinimo);
            attrs.addFlashAttribute(ATTR_OK, "Stock de «" + insumo.getNombre() + "» actualizado.");
        } catch (IllegalArgumentException ex) {
            attrs.addFlashAttribute(ATTR_ERROR, ex.getMessage());
        }
        return REDIRECT_INVENTARIO;
    }

    @PostMapping("/insumos/{id}/desactivar") public String desactivarInsumo(@PathVariable Long id, RedirectAttributes attrs) {
        try {
            service.desactivar(id);
            attrs.addFlashAttribute(ATTR_OK, "Insumo eliminado del inventario y retirado de las recetas.");
        } catch (IllegalArgumentException ex) {
            attrs.addFlashAttribute(ATTR_ERROR, ex.getMessage());
        }
        return REDIRECT_INVENTARIO;
    }

    @PostMapping("/recetas") public String guardarReceta(@RequestParam Integer menuId, @RequestParam Long insumoId, @RequestParam BigDecimal cantidad,
            RedirectAttributes attrs) {
        if (cantidad.signum() <= 0 || cantidad.compareTo(MAXIMO) > 0) return error(attrs, "La cantidad por unidad debe ser mayor que cero.");
        try {
            Insumo insumo = service.buscar(insumoId);
            Menu menu = menus.findById(menuId).orElseThrow(() -> new IllegalArgumentException("Producto no encontrado: " + menuId));
            service.guardarReceta(MenuInsumo.builder().menu(menu).insumo(insumo).cantidad(cantidad).build());
            attrs.addFlashAttribute(ATTR_OK, "Receta de «" + menu.getProducto() + "» guardada con " + insumo.getNombre() + ".");
        } catch (IllegalArgumentException ex) {
            attrs.addFlashAttribute(ATTR_ERROR, ex.getMessage());
        }
        return REDIRECT_INVENTARIO;
    }

    @PostMapping("/recetas/{id}/eliminar") public String eliminarReceta(@PathVariable Long id, RedirectAttributes attrs) {
        service.eliminarReceta(id);
        attrs.addFlashAttribute(ATTR_OK, "Ingrediente retirado de la receta.");
        return REDIRECT_INVENTARIO;
    }

    private String error(RedirectAttributes attrs, String mensaje) {
        attrs.addFlashAttribute(ATTR_ERROR, mensaje);
        return REDIRECT_INVENTARIO;
    }

    private String validarStocks(BigDecimal stockActual, BigDecimal stockMinimo) {
        if (stockActual.signum() < 0 || stockMinimo.signum() < 0) return "El stock actual y el mínimo no pueden ser negativos.";
        if (stockActual.compareTo(MAXIMO) > 0 || stockMinimo.compareTo(MAXIMO) > 0) return "El valor de stock excede el máximo permitido.";
        return null;
    }
}
