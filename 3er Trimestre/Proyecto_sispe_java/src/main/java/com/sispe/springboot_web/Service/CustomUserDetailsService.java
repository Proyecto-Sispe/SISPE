package com.sispe.springboot_web.Service;

import java.util.Locale;
import java.util.stream.Collectors;

import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

import com.sispe.springboot_web.Model.Persona;
import com.sispe.springboot_web.Repository.PersonaRepository;

@Service
public class CustomUserDetailsService implements UserDetailsService {

    private final PersonaRepository personaRepository;

    public CustomUserDetailsService(PersonaRepository personaRepository) {
        this.personaRepository = personaRepository;
    }

    @Override
    public UserDetails loadUserByUsername(String correo) throws UsernameNotFoundException {
        Persona persona = personaRepository.findByCorreo(correo)
                .orElseThrow(() -> new UsernameNotFoundException("Persona no encontrado con el correo: " + correo));

        return new User(
                persona.getCorreo(),
                persona.getPassword(),
                persona.getEstado() != null && persona.getEstado() == 1,
                true, true, true,
                persona.getRoles().stream()
                        // Agregamos ROLE_ y lo pasamos a mayúsculas para evitar errores de tipeo
                        .map(rol -> new SimpleGrantedAuthority("ROLE_" + rol.getNombre().toUpperCase(Locale.ROOT)))
                        .collect(Collectors.toList())
        );
    }
}