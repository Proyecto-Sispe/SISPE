package com.sispe.springboot_web.Service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.List;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.sispe.springboot_web.Model.Menu;
import com.sispe.springboot_web.Repository.MenuRepository;

@ExtendWith(MockitoExtension.class)
class MenuServiceTest {

    @Mock
    private MenuRepository repository;

    private MenuService menuService;

    @BeforeEach
    void setUp() {
        menuService = new MenuService(repository);
    }

    @Test
    void listarDevuelveProductosDelRepositorio() {
        List<Menu> productos = List.of(new Menu());
        when(repository.findAll()).thenReturn(productos);

        assertEquals(productos, menuService.listar());
    }

    @Test
    void guardarPersisteProducto() {
        Menu menu = new Menu();
        when(repository.save(menu)).thenReturn(menu);

        assertEquals(menu, menuService.guardar(menu));
        verify(repository).save(menu);
    }

    @Test
    void eliminarBorraPorId() {
        menuService.eliminar(9);

        verify(repository).deleteById(9);
    }
}
