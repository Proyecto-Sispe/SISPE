package com.sispe.springboot_web.Service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.time.LocalDateTime;
import java.util.Optional;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.security.crypto.password.PasswordEncoder;

import com.sispe.springboot_web.Model.PasswordReset;
import com.sispe.springboot_web.Model.Persona;
import com.sispe.springboot_web.Repository.PasswordResetRepository;
import com.sispe.springboot_web.Repository.PersonaRepository;

@ExtendWith(MockitoExtension.class)
class PasswordResetServiceTest {

    @Mock
    private PersonaRepository personaRepository;

    @Mock
    private PasswordResetRepository resetRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @Mock
    private JavaMailSender mailSender;

    private PasswordResetService passwordResetService;

    @BeforeEach
    void setUp() {
        passwordResetService = new PasswordResetService(
                personaRepository, resetRepository, passwordEncoder, mailSender);
    }

    @Test
    void solicitarCodigoNoEnviaCorreoSiPersonaNoExiste() {
        when(personaRepository.findByCorreo("ausente@sispe.test")).thenReturn(Optional.empty());

        passwordResetService.solicitarCodigo(" ausente@sispe.test ");

        verify(resetRepository, org.mockito.Mockito.never()).save(any());
        verify(mailSender, org.mockito.Mockito.never()).send(any(SimpleMailMessage.class));
    }

    @Test
    void restablecerPasswordActualizaPersonaYMarcaCodigoComoUsado() {
        Persona persona = new Persona();
        persona.setCorreo("usuario@sispe.test");
        PasswordReset reset = PasswordReset.builder()
                .correo(persona.getCorreo())
                .codigo("123456")
                .expira(LocalDateTime.now().plusMinutes(5))
                .usado(false)
                .build();
        when(resetRepository.findFirstByCorreoAndUsadoFalseOrderByCreatedAtDesc(persona.getCorreo()))
                .thenReturn(Optional.of(reset));
        when(personaRepository.findByCorreo(persona.getCorreo())).thenReturn(Optional.of(persona));
        when(passwordEncoder.encode("nueva")).thenReturn("hash-nueva");

        passwordResetService.restablecerPassword(persona.getCorreo(), "123456", "nueva");

        assertEquals("hash-nueva", persona.getPassword());
        assertEquals(true, reset.getUsado());
        verify(personaRepository).save(persona);
        verify(resetRepository).save(reset);
    }

    @Test
    void restablecerPasswordRechazaCodigoIncorrecto() {
        PasswordReset reset = PasswordReset.builder()
                .codigo("123456")
                .expira(LocalDateTime.now().plusMinutes(5))
                .usado(false)
                .build();
        when(resetRepository.findFirstByCorreoAndUsadoFalseOrderByCreatedAtDesc("usuario@sispe.test"))
                .thenReturn(Optional.of(reset));

        IllegalArgumentException error = assertThrows(IllegalArgumentException.class,
                () -> passwordResetService.restablecerPassword(
                        "usuario@sispe.test", "000000", "nueva"));

        assertEquals("El código ingresado no es correcto.", error.getMessage());
    }

    @Test
    void restablecerPasswordRechazaCodigoExpirado() {
        PasswordReset reset = PasswordReset.builder()
                .codigo("123456")
                .expira(LocalDateTime.now().minusMinutes(1))
                .usado(false)
                .build();
        when(resetRepository.findFirstByCorreoAndUsadoFalseOrderByCreatedAtDesc("usuario@sispe.test"))
                .thenReturn(Optional.of(reset));

        IllegalArgumentException error = assertThrows(IllegalArgumentException.class,
                () -> passwordResetService.restablecerPassword(
                        "usuario@sispe.test", "123456", "nueva"));

        assertEquals("El código expiró. Solicita uno nuevo.", error.getMessage());
    }
}
