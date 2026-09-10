package com.sispe.springboot_web.controller;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import java.util.List;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.ui.Model;

import com.sispe.springboot_web.model.Persona;
import com.sispe.springboot_web.model.Rol;
import com.sispe.springboot_web.repository.PersonaRepository;
import com.sispe.springboot_web.repository.RolRepository;
import com.sispe.springboot_web.service.AuthService;
import com.sispe.springboot_web.dto.PersonaDTO;
import com.sispe.springboot_web.mapper.PersonaMapper;

import org.springframework.validation.BindingResult;

@ExtendWith(MockitoExtension.class)
class AdminControllerTest {

    @Mock
    private AuthService authService;

    @Mock
    private RolRepository rolRepository;

    @Mock
    private PersonaRepository personaRepository;

    @Mock
    private PersonaMapper personaMapper;

    @Mock
    private BindingResult bindingResult;

    @Mock
    private Model model;

    private AdminController controller;

    @BeforeEach
    void setUp() {
        controller = new AdminController(authService, rolRepository, personaRepository, personaMapper);
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
        PersonaDTO dto = new PersonaDTO();
        Persona persona = new Persona();
        when(bindingResult.hasErrors()).thenReturn(false);
        when(personaMapper.toEntity(dto)).thenReturn(persona);

        assertEquals("redirect:/inicio?creado",
                controller.guardarPersonaConRol(dto, bindingResult, 2, model));
        verify(authService).registrarConRol(persona, 2);
    }

    @Test
    void guardarPersonaConErroresVuelveAlFormulario() {
        PersonaDTO dto = new PersonaDTO();
        List<Rol> roles = List.of(new Rol());
        when(bindingResult.hasErrors()).thenReturn(true);
        when(rolRepository.findAll()).thenReturn(roles);

        assertEquals("admin/crear-usuario",
                controller.guardarPersonaConRol(dto, bindingResult, 2, model));
        verify(model).addAttribute("roles", roles);
        verifyNoInteractions(authService);
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
