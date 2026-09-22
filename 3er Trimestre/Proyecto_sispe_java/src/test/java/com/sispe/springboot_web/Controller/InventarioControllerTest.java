package com.sispe.springboot_web.Controller;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.math.BigDecimal;
import java.util.Optional;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.ui.Model;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import com.sispe.springboot_web.Model.Insumo;
import com.sispe.springboot_web.Model.Menu;
import com.sispe.springboot_web.Model.MenuInsumo;
import com.sispe.springboot_web.Repository.MenuRepository;
import com.sispe.springboot_web.Service.InventarioService;

@ExtendWith(MockitoExtension.class)
class InventarioControllerTest {

    @Mock
    private InventarioService service;

    @Mock
    private MenuRepository menus;

    @Mock
    private Model model;

    @Mock
    private RedirectAttributes attrs;

    private InventarioController controller;

    @BeforeEach
    void setUp() {
        controller = new InventarioController(service, menus);
    }

    @Test
    void indexCargaInsumosRecetasYMenu() {
        when(service.listar()).thenReturn(java.util.List.of());
        when(service.recetas()).thenReturn(java.util.List.of());
        when(menus.findAll()).thenReturn(java.util.List.of());

        assertEquals("admin/inventario", controller.index(model));
        verify(model).addAttribute("insumos", java.util.List.of());
        verify(model).addAttribute("recetas", java.util.List.of());
        verify(model).addAttribute("menus", java.util.List.of());
    }

    @Test
    void guardarInsumoRechazaNombreVacio() {
        String vista = controller.guardarInsumo("  ", BigDecimal.TEN, BigDecimal.ONE, "kg", attrs);

        assertEquals("redirect:/admin/inventario", vista);
        verify(attrs).addFlashAttribute("error", "El nombre y la unidad del insumo son obligatorios.");
        verify(service, never()).guardar(any());
    }

    @Test
    void guardarInsumoRechazaStockNegativo() {
        controller.guardarInsumo("Queso", new BigDecimal("-1"), BigDecimal.ONE, "kg", attrs);

        verify(attrs).addFlashAttribute("error", "El stock actual y el mínimo no pueden ser negativos.");
        verify(service, never()).guardar(any());
    }

    @Test
    void guardarInsumoValidoLoPersiste() {
        controller.guardarInsumo("Queso", new BigDecimal("10.000"), new BigDecimal("2.000"), "kg", attrs);

        verify(service).guardar(any(Insumo.class));
        verify(attrs).addFlashAttribute("ok", "Insumo «Queso» guardado correctamente.");
    }

    @Test
    void guardarInsumoDuplicadoMuestraMensajeAmigable() {
        when(service.guardar(any())).thenThrow(new DataIntegrityViolationException("uq_insumo_nombre"));

        controller.guardarInsumo("Queso", BigDecimal.TEN, BigDecimal.ONE, "kg", attrs);

        verify(attrs).addFlashAttribute("error",
                "No se pudo guardar el insumo. Es posible que ya exista uno con el nombre «Queso».");
    }

    @Test
    void actualizarInsumoRechazaStockQueSuperaElMaximoDeLaColumna() {
        controller.actualizarInsumo(1L, new BigDecimal("9999999999"), BigDecimal.ONE, attrs);

        verify(attrs).addFlashAttribute("error", "El valor de stock excede el máximo permitido.");
        verify(service, never()).actualizar(any(), any(), any());
    }

    @Test
    void actualizarInsumoValidoDelegaEnElServicio() {
        Insumo insumo = Insumo.builder().id(1L).nombre("Queso").build();
        when(service.actualizar(1L, new BigDecimal("5"), new BigDecimal("1"))).thenReturn(insumo);

        controller.actualizarInsumo(1L, new BigDecimal("5"), new BigDecimal("1"), attrs);

        verify(attrs).addFlashAttribute("ok", "Stock de «Queso» actualizado.");
    }

    @Test
    void desactivarInsumoInexistenteMuestraElErrorDelServicio() {
        org.mockito.Mockito.doThrow(new IllegalArgumentException("Insumo no encontrado: 99"))
                .when(service).desactivar(99L);

        controller.desactivarInsumo(99L, attrs);

        verify(attrs).addFlashAttribute("error", "Insumo no encontrado: 99");
    }

    @Test
    void guardarRecetaRechazaCantidadCero() {
        controller.guardarReceta(1, 1L, BigDecimal.ZERO, attrs);

        verify(attrs).addFlashAttribute("error", "La cantidad por unidad debe ser mayor que cero.");
        verify(service, never()).guardarReceta(any());
    }

    @Test
    void guardarRecetaRechazaProductoInexistente() {
        Insumo insumo = Insumo.builder().id(1L).nombre("Queso").build();
        when(service.buscar(1L)).thenReturn(insumo);
        when(menus.findById(77)).thenReturn(Optional.empty());

        controller.guardarReceta(77, 1L, BigDecimal.ONE, attrs);

        verify(attrs).addFlashAttribute("error", "Producto no encontrado: 77");
        verify(service, never()).guardarReceta(any());
    }

    @Test
    void guardarRecetaValidaDelegaEnElServicio() {
        Insumo insumo = Insumo.builder().id(1L).nombre("Queso").build();
        Menu menu = Menu.builder().id(5).producto("Hamburguesa").build();
        when(service.buscar(1L)).thenReturn(insumo);
        when(menus.findById(5)).thenReturn(Optional.of(menu));

        controller.guardarReceta(5, 1L, new BigDecimal("2"), attrs);

        verify(service).guardarReceta(any(MenuInsumo.class));
        verify(attrs).addFlashAttribute("ok", "Receta de «Hamburguesa» guardada con Queso.");
    }

    @Test
    void eliminarRecetaDelegaEnElServicio() {
        controller.eliminarReceta(9L, attrs);

        verify(service).eliminarReceta(9L);
        verify(attrs).addFlashAttribute("ok", "Ingrediente retirado de la receta.");
    }
}
