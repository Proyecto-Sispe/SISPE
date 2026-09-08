package com.sispe.springboot_web.Service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.when;

import java.util.Optional;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UsernameNotFoundException;

import com.sispe.springboot_web.Model.Persona;
import com.sispe.springboot_web.Model.Rol;
import com.sispe.springboot_web.Repository.PersonaRepository;

@ExtendWith(MockitoExtension.class)
class CustomUserDetailsServiceTest {

    @Mock
    private PersonaRepository personaRepository;

    @Test
    void cargaUsuarioConRolesNormalizados() {
        Persona persona = new Persona();
        persona.setCorreo("usuario@sispe.test");
        persona.setPassword("hash");
        persona.setEstado(1);
        Rol rol = new Rol();
        rol.setNombre("Administrador");
        persona.getRoles().add(rol);
        when(personaRepository.findByCorreo(persona.getCorreo())).thenReturn(Optional.of(persona));

        UserDetails details = new CustomUserDetailsService(personaRepository)
                .loadUserByUsername(persona.getCorreo());

        assertEquals("usuario@sispe.test", details.getUsername());
        assertEquals("hash", details.getPassword());
        assertEquals("ROLE_ADMINISTRADOR", details.getAuthorities().iterator().next().getAuthority());
        assertEquals(true, details.isEnabled());
    }

    @Test
    void rechazaUsuarioNoEncontrado() {
        when(personaRepository.findByCorreo("ausente@sispe.test")).thenReturn(Optional.empty());

        assertThrows(UsernameNotFoundException.class,
                () -> new CustomUserDetailsService(personaRepository)
                        .loadUserByUsername("ausente@sispe.test"));
    }
}
