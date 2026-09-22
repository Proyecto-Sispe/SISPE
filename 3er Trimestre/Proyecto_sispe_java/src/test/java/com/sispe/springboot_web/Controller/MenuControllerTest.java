package com.sispe.springboot_web.Controller;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.List;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.ui.Model;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import com.sispe.springboot_web.Model.Categoria;
import com.sispe.springboot_web.Model.Menu;
import com.sispe.springboot_web.Repository.AdicionRepository;
import com.sispe.springboot_web.Repository.CategoriaRepository;
import com.sispe.springboot_web.Service.MenuService;

@ExtendWith(MockitoExtension.class)
class MenuControllerTest {

    @Mock
    private MenuService service;

    @Mock
    private CategoriaRepository categorias;

    @Mock
    private AdicionRepository adiciones;

    @Mock
    private Model model;

    @Mock
    private RedirectAttributes attributes;

    private MenuController controller;

    /** Un MultipartFile "vacío" para simular que el formulario no subió foto nueva. */
    private final MultipartFile sinFoto = mock(MultipartFile.class);

    @BeforeEach
    void setUp() {
        controller = new MenuController(service, categorias, adiciones);
        when(sinFoto.isEmpty()).thenReturn(true);
    }

    @Test
    void indexCargaProductosCategoriasYMenu() {
        List<Menu> productos = List.of(new Menu());
        List<Categoria> categoriasDisponibles = List.of(new Categoria());
        when(service.listar()).thenReturn(productos);
        when(categorias.findAll()).thenReturn(categoriasDisponibles);

        assertEquals("menu/index", controller.index(model));
        verify(model).addAttribute("productos", productos);
        verify(model).addAttribute("categorias", categoriasDisponibles);
    }

    @Test
    void digitalCargaProductosYAdiciones() {
        List<Menu> productos = List.of(new Menu());
        when(service.listar()).thenReturn(productos);

        assertEquals("menu/digital", controller.digital(model));
        verify(model).addAttribute("productos", productos);
    }

    @Test
    void guardarRechazaCategoriaInexistente() {
        Menu menu = new Menu();

        assertEquals("redirect:/menu", controller.guardar(menu, sinFoto, attributes));
        verify(attributes).addFlashAttribute("error", "Selecciona una categoría registrada en MySQL.");
    }

    @Test
    void guardarPersisteCategoriaValida() {
        Menu menu = new Menu();
        Categoria categoria = new Categoria();
        categoria.setId(8);
        menu.setCategoria(categoria);
        when(categorias.existsById(8)).thenReturn(true);

        assertEquals("redirect:/menu", controller.guardar(menu, sinFoto, attributes));
        verify(service).guardar(menu);
    }

    @Test
    void eliminarRedirige() {
        assertEquals("redirect:/menu", controller.eliminar(5));
        verify(service).eliminar(5);
    }

    @Test
    void actualizarAsignaIdYGuarda() {
        Menu menu = new Menu();
        Categoria categoria = new Categoria();
        categoria.setId(8);
        menu.setCategoria(categoria);
        when(categorias.existsById(8)).thenReturn(true);

        assertEquals("redirect:/menu", controller.actualizar(11, menu, sinFoto, attributes));
        assertEquals(11, menu.getId());
        verify(service).guardar(menu);
    }
}