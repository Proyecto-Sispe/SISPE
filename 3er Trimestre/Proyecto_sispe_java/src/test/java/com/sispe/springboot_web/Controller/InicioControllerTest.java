package com.sispe.springboot_web.Controller;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.Optional;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.ui.Model;

import com.sispe.springboot_web.Model.Persona;
import com.sispe.springboot_web.Repository.PersonaRepository;

@ExtendWith(MockitoExtension.class)
class InicioControllerTest {

    @Mock
    private PersonaRepository personaRepository;

    @Mock
    private Model model;

    private InicioController controller;

    @BeforeEach
    void setUp() {
        controller = new InicioController(personaRepository);
    }

    @Test
    void accesoDenegadoMuestraVista() {
        assertEquals("acceso-denegado", controller.accesoDenegado());
    }

    @Test
    void inicioSinUsuarioNoConsultaRepositorio() {
        assertEquals("inicio", controller.inicio(null, model));
    }

    @Test
    void inicioConUsuarioAgregaPersona() {
        UserDetails user = User.withUsername("usuario@test.com").password("hash").roles("CLIENTE").build();
        Persona persona = new Persona();
        when(personaRepository.findByCorreo("usuario@test.com")).thenReturn(Optional.of(persona));

        assertEquals("inicio", controller.inicio(user, model));
        verify(model).addAttribute("persona", persona);
    }
}
