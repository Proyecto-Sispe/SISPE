package com.sispe.springboot_web.Controller;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.List;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.ui.Model;

import com.sispe.springboot_web.Model.Persona;
import com.sispe.springboot_web.Model.Rol;
import com.sispe.springboot_web.Repository.PersonaRepository;
import com.sispe.springboot_web.Repository.RolRepository;
import com.sispe.springboot_web.Service.AuthService;

@ExtendWith(MockitoExtension.class)
class AdminControllerTest {

    @Mock
    private AuthService authService;

    @Mock
    private RolRepository rolRepository;

    @Mock
    private PersonaRepository personaRepository;

    @Mock
    private Model model;

    private AdminController controller;

    @BeforeEach
    void setUp() {
        controller = new AdminController(authService, rolRepository, personaRepository);
    }

    @Test
    void formularioNuevoCargaPersonaYRoles() {
        List<Rol> roles = List.of(new Rol());
        when(rolRepository.findAll()).thenReturn(roles);

        assertEquals("admin/crear-usuario", controller.formularioNuevoPersona(model));
        verify(model).addAttribute("roles", roles);
    }

    @Test
    void guardarPersonaRedirige() {
        Persona persona = new Persona();

        assertEquals("redirect:/inicio?creado", controller.guardarPersonaConRol(persona, 2));
        verify(authService).registrarConRol(persona, 2);
    }

    @Test
    void listarUsuariosCargaUsuariosYRoles() {
        List<Persona> usuarios = List.of(new Persona());
        List<Rol> roles = List.of(new Rol());
        when(personaRepository.findAll()).thenReturn(usuarios);
        when(rolRepository.findAll()).thenReturn(roles);

        assertEquals("admin/listar-usuarios", controller.listarUsuarios(model));
        verify(model).addAttribute("usuarios", usuarios);
        verify(model).addAttribute("roles", roles);
    }

    @Test
    void cambiarRolRedirige() {
        assertEquals("redirect:/admin/usuarios?actualizado", controller.cambiarRol(1, 2, 3));
        verify(authService).cambiarRol(1, 2, 3);
    }
}
