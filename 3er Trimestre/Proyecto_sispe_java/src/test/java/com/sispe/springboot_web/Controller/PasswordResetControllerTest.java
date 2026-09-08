package com.sispe.springboot_web.Controller;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.mockito.Mockito.doThrow;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.ui.Model;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import com.sispe.springboot_web.Service.PasswordResetService;

@ExtendWith(MockitoExtension.class)
class PasswordResetControllerTest {

    @Mock
    private PasswordResetService resetService;

    @Mock
    private RedirectAttributes attributes;

    @Mock
    private Model model;

    private PasswordResetController controller;

    @BeforeEach
    void setUp() {
        controller = new PasswordResetController(resetService);
    }

    @Test
    void formularioOlvideMuestraVista() {
        assertEquals("olvide-password", controller.formularioOlvide());
    }

    @Test
    void enviarCodigoPreparaRedireccion() {
        assertEquals("redirect:/login/verificar", controller.enviarCodigo(" usuario@test.com ", attributes));
        verify(resetService).solicitarCodigo(" usuario@test.com ");
        verify(attributes).addFlashAttribute("mensaje", "Si el correo está registrado, te enviamos un código de verificación.");
        verify(attributes).addAttribute("correo", " usuario@test.com ");
    }

    @Test
    void formularioVerificarAgregaCorreo() {
        assertEquals("verificar-codigo", controller.formularioVerificar("usuario@test.com", model));
        verify(model).addAttribute("correo", "usuario@test.com");
    }

    @Test
    void restablecerExitosoRedirige() {
        assertEquals("redirect:/login?recuperado",
                controller.restablecer("usuario@test.com", "123456", "nueva", model));
        verify(resetService).restablecerPassword("usuario@test.com", "123456", "nueva");
    }

    @Test
    void restablecerConErrorMuestraVerificacion() {
        doThrow(new IllegalArgumentException("código incorrecto"))
            .when(resetService).restablecerPassword("usuario@test.com", "000000", "nueva");

        assertEquals("verificar-codigo",
                controller.restablecer("usuario@test.com", "000000", "nueva", model));
        verify(model).addAttribute("error", "código incorrecto");
        verify(model).addAttribute("correo", "usuario@test.com");
    }
}
