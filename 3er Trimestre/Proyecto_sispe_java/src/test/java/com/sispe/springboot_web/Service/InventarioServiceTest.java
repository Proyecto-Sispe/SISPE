package com.sispe.springboot_web.Service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.sispe.springboot_web.Model.DetallePedido;
import com.sispe.springboot_web.Model.Insumo;
import com.sispe.springboot_web.Model.Menu;
import com.sispe.springboot_web.Model.MenuInsumo;
import com.sispe.springboot_web.Repository.DetallePedidoRepository;
import com.sispe.springboot_web.Repository.InsumoRepository;
import com.sispe.springboot_web.Repository.MenuInsumoRepository;

@ExtendWith(MockitoExtension.class)
class InventarioServiceTest {

    @Mock
    private InsumoRepository insumos;

    @Mock
    private MenuInsumoRepository recetas;

    @Mock
    private DetallePedidoRepository detalles;

    private InventarioService inventarioService;
    private Menu menu;
    private Insumo insumo;

    @BeforeEach
    void setUp() {
        inventarioService = new InventarioService(insumos, recetas, detalles);
        menu = Menu.builder().id(5).producto("Pizza").build();
        insumo = Insumo.builder()
                .id(9L)
                .nombre("Queso")
                .stockActual(new BigDecimal("10.000"))
                .stockMinimo(new BigDecimal("2.000"))
                .unidad("Kg")
                .build();
    }

    @Test
    void descontarPedidoAcumulaConsumoYGuardaStockActualizado() {
        DetallePedido detalle = DetallePedido.builder().pedidoId(3L).menu(menu).cantidad(2).build();
        MenuInsumo receta = MenuInsumo.builder().menu(menu).insumo(insumo).cantidad(new BigDecimal("1.5")).build();
        when(detalles.findByPedidoId(3L)).thenReturn(List.of(detalle));
        when(recetas.findByMenu_Id(5)).thenReturn(List.of(receta));
        when(insumos.findById(9L)).thenReturn(Optional.of(insumo));

        inventarioService.descontarPedido(3L);

        assertEquals(new BigDecimal("7.000"), insumo.getStockActual());
        verify(insumos).saveAll(any());
    }

    @Test
    void descontarPedidoRechazaStockInsuficiente() {
        DetallePedido detalle = DetallePedido.builder().menu(menu).cantidad(8).build();
        MenuInsumo receta = MenuInsumo.builder().menu(menu).insumo(insumo).cantidad(new BigDecimal("2")).build();
        when(detalles.findByPedidoId(3L)).thenReturn(List.of(detalle));
        when(recetas.findByMenu_Id(5)).thenReturn(List.of(receta));
        when(insumos.findById(9L)).thenReturn(Optional.of(insumo));

        IllegalStateException error = assertThrows(IllegalStateException.class,
                () -> inventarioService.descontarPedido(3L));

        assertEquals("Stock insuficiente para: Queso", error.getMessage());
    }

    @Test
    void descontarPedidoRechazaInsumoInexistente() {
        DetallePedido detalle = DetallePedido.builder().menu(menu).cantidad(1).build();
        MenuInsumo receta = MenuInsumo.builder().menu(menu).insumo(insumo).cantidad(BigDecimal.ONE).build();
        when(detalles.findByPedidoId(3L)).thenReturn(List.of(detalle));
        when(recetas.findByMenu_Id(5)).thenReturn(List.of(receta));
        when(insumos.findById(9L)).thenReturn(Optional.empty());

        assertThrows(IllegalStateException.class, () -> inventarioService.descontarPedido(3L));
    }

    @Test
    void guardarRecetaActualizaExistenteOCreaNueva() {
        MenuInsumo existente = MenuInsumo.builder().menu(menu).insumo(insumo).cantidad(BigDecimal.ONE).build();
        MenuInsumo nueva = MenuInsumo.builder().menu(menu).insumo(insumo).cantidad(new BigDecimal("2")).build();
        when(recetas.findByMenu_IdAndInsumo_Id(5, 9L)).thenReturn(Optional.of(existente), Optional.empty());
        when(recetas.save(any(MenuInsumo.class))).thenAnswer(invocation -> invocation.getArgument(0));

        MenuInsumo actualizada = inventarioService.guardarReceta(nueva);
        MenuInsumo creada = inventarioService.guardarReceta(nueva);

        assertSame(existente, actualizada);
        assertEquals(new BigDecimal("2"), existente.getCantidad());
        assertSame(nueva, creada);
    }

    @Test
    void exponeOperacionesDeInsumosYRecetas() {
        when(insumos.save(insumo)).thenReturn(insumo);
        when(insumos.findById(9L)).thenReturn(Optional.of(insumo));
        when(insumos.findByActivoTrueOrderByNombreAsc()).thenReturn(List.of(insumo));
        when(recetas.findByMenu_Id(5)).thenReturn(List.of());
        when(recetas.findAll()).thenReturn(List.of());

        assertSame(insumo, inventarioService.guardar(insumo));
        assertSame(insumo, inventarioService.buscar(9L));
        assertEquals(List.of(insumo), inventarioService.listar());
        assertEquals(List.of(), inventarioService.receta(5));
        assertEquals(List.of(), inventarioService.recetas());
        verify(insumos).save(insumo);
    }

    @Test
    void buscarRechazaInsumoDesconocido() {
        when(insumos.findById(99L)).thenReturn(Optional.empty());

        IllegalArgumentException error = assertThrows(IllegalArgumentException.class,
                () -> inventarioService.buscar(99L));

        assertEquals("Insumo no encontrado: 99", error.getMessage());
    }
}
