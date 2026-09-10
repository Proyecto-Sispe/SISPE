package com.sispe.springboot_web.controller;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.List;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.sispe.springboot_web.model.Menu;
import com.sispe.springboot_web.service.MenuService;

@ExtendWith(MockitoExtension.class)
class MenuApiControllerTest {

    @Mock
    private MenuService service;

    private MenuApiController controller;

    @BeforeEach
    void setUp() {
        controller = new MenuApiController(service);
    }

    @Test
    void listarDevuelveMenu() {
        List<Menu> menu = List.of(new Menu());
        when(service.listar()).thenReturn(menu);

        assertEquals(menu, controller.listar());
    }

    @Test
    void crearGuardaMenu() {
        Menu menu = new Menu();
        when(service.guardar(menu)).thenReturn(menu);

        assertEquals(menu, controller.crear(menu));
        verify(service).guardar(menu);
    }

    @Test
    void eliminarDelegaServicio() {
        controller.eliminar(4);

        verify(service).eliminar(4);
    }
}
