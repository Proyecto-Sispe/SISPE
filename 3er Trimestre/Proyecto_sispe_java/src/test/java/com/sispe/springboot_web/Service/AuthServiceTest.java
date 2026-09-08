package com.sispe.springboot_web.Service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.Optional;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.password.PasswordEncoder;

import com.sispe.springboot_web.Model.Persona;
import com.sispe.springboot_web.Model.PersonaId;
import com.sispe.springboot_web.Model.Rol;
import com.sispe.springboot_web.Repository.PersonaRepository;
import com.sispe.springboot_web.Repository.RolRepository;

@ExtendWith(MockitoExtension.class)
class AuthServiceTest {

    @Mock
    private PersonaRepository personaRepository;

    @Mock
    private RolRepository rolRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    private AuthService authService;

    @BeforeEach
    void setUp() {
        authService = new AuthService(personaRepository, rolRepository, passwordEncoder);
    }

    @Test
    void registrarAsignaRolClienteYGuardaPasswordCodificada() {
        Persona persona = new Persona();
        persona.setCorreo("cliente@sispe.test");
        persona.setPassword("secreto");
        Rol cliente = rol(4, "Cliente");

        when(personaRepository.existsByCorreo(persona.getCorreo())).thenReturn(false);
        when(passwordEncoder.encode("secreto")).thenReturn("hash");
        when(rolRepository.findById(4)).thenReturn(Optional.of(cliente));
        when(personaRepository.save(persona)).thenReturn(persona);

        Persona resultado = authService.registrar(persona);

        assertEquals(persona, resultado);
        assertEquals("hash", persona.getPassword());
        assertEquals(1, persona.getEstado());
        assertEquals(1, persona.getRoles().size());
        assertEquals(cliente, persona.getRoles().iterator().next());
        verify(personaRepository).save(persona);
    }

    @Test
    void registrarRechazaCorreoDuplicado() {
        Persona persona = new Persona();
        persona.setCorreo("repetido@sispe.test");
        when(personaRepository.existsByCorreo(persona.getCorreo())).thenReturn(true);

        IllegalArgumentException error = assertThrows(IllegalArgumentException.class,
                () -> authService.registrar(persona));

        assertEquals("El correo ya está registrado", error.getMessage());
    }

    @Test
    void registrarRechazaRolInexistente() {
        Persona persona = new Persona();
        persona.setCorreo("nuevo@sispe.test");
        persona.setPassword("secreto");
        when(personaRepository.existsByCorreo(persona.getCorreo())).thenReturn(false);
        when(passwordEncoder.encode("secreto")).thenReturn("hash");
        when(rolRepository.findById(4)).thenReturn(Optional.empty());

        IllegalArgumentException error = assertThrows(IllegalArgumentException.class,
                () -> authService.registrar(persona));

        assertEquals("El rol seleccionado no existe", error.getMessage());
    }

    @Test
    void cambiarRolReemplazaRolesExistentes() {
        Persona persona = new Persona();
        persona.setIdUsuario(7);
        persona.setTipoDocumento(1);
        persona.getRoles().add(rol(2, "Administrador"));
        Rol nuevoRol = rol(3, "Mesero");
        PersonaId id = new PersonaId(7, 1);

        when(personaRepository.findById(id)).thenReturn(Optional.of(persona));
        when(rolRepository.findById(3)).thenReturn(Optional.of(nuevoRol));
        when(personaRepository.save(persona)).thenReturn(persona);

        authService.cambiarRol(7, 1, 3);

        assertEquals(1, persona.getRoles().size());
        assertEquals(nuevoRol, persona.getRoles().iterator().next());
        verify(personaRepository).save(persona);
    }

    @Test
    void cambiarRolRechazaPersonaInexistente() {
        when(personaRepository.findById(new PersonaId(7, 1))).thenReturn(Optional.empty());

        IllegalArgumentException error = assertThrows(IllegalArgumentException.class,
                () -> authService.cambiarRol(7, 1, 3));

        assertEquals("Persona no encontrada", error.getMessage());
    }

    private Rol rol(Integer id, String nombre) {
        Rol rol = new Rol();
        rol.setIdRol(id);
        rol.setNombre(nombre);
        return rol;
    }
}
