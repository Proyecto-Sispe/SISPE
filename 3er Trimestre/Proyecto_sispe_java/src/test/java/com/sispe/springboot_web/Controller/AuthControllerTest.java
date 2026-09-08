package com.sispe.springboot_web.Controller;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.ui.Model;

import com.sispe.springboot_web.Model.Persona;
import com.sispe.springboot_web.Service.AuthService;

@ExtendWith(MockitoExtension.class)
class AuthControllerTest {

    @Mock
    private AuthService authService;

    @Mock
    private Model model;

    private AuthController controller;

    @BeforeEach
    void setUp() {
        controller = new AuthController(authService);
    }

    @Test
    void loginMuestraVista() {
        assertEquals("login", controller.login());
    }

    @Test
    void mostrarRegistroPreparaPersona() {
        assertEquals("registro", controller.mostrarRegistro(model));
        verify(model).addAttribute(org.mockito.ArgumentMatchers.eq("persona"), org.mockito.ArgumentMatchers.any(Persona.class));
    }

    @Test
    void registrarExitosoRedirigeAlLogin() {
        Persona persona = new Persona();

        assertEquals("redirect:/login?registrado", controller.registrar(persona, model));
        verify(authService).registrar(persona);
    }

    @Test
    void registrarConErrorMuestraMensaje() {
        Persona persona = new Persona();
        when(authService.registrar(persona)).thenThrow(new IllegalArgumentException("correo duplicado"));

        assertEquals("registro", controller.registrar(persona, model));
        verify(model).addAttribute("error", "correo duplicado");
    }
}
