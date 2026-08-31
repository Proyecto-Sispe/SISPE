package com.sispe.springboot_web.Service;

import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import com.sispe.springboot_web.Model.Rol;
import com.sispe.springboot_web.Model.Persona;
import com.sispe.springboot_web.Model.PersonaId;
import com.sispe.springboot_web.Repository.RolRepository;
import com.sispe.springboot_web.Repository.PersonaRepository;

@Service
public class AuthService {

    private final PersonaRepository personaRepository;
    private final RolRepository rolRepository;
    private final PasswordEncoder passwordEncoder;

    public AuthService(PersonaRepository personaRepository, RolRepository rolRepository, PasswordEncoder passwordEncoder) {
        this.personaRepository = personaRepository;
        this.rolRepository = rolRepository;
        this.passwordEncoder = passwordEncoder;
    }

    // Usado por AuthController para autoregistro de Clientes (Rol ID: 4)
    public Persona registrar(Persona persona) {
        return registrarConRol(persona, 4);
    }

    // Usado por AdminController para crear usuarios asignando cualquier rol
    public Persona registrarConRol(Persona persona, Integer idRol) {
        if (personaRepository.existsByCorreo(persona.getCorreo())) {
            throw new IllegalArgumentException("El correo ya está registrado");
        }

        persona.setPassword(passwordEncoder.encode(persona.getPassword()));
        persona.setEstado(1);

        Rol rol = rolRepository.findById(idRol)
                .orElseThrow(() -> new IllegalArgumentException("El rol seleccionado no existe"));

        persona.getRoles().add(rol);

        return personaRepository.save(persona);
    }

    // Usado por AdminController para cambiar el rol de un usuario ya existente
    public Persona cambiarRol(Integer idUsuario, Integer tipoDocumento, Integer nuevoIdRol) {
        PersonaId id = new PersonaId(idUsuario, tipoDocumento);

        Persona persona = personaRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Persona no encontrada"));

        Rol rol = rolRepository.findById(nuevoIdRol)
                .orElseThrow(() -> new IllegalArgumentException("El rol seleccionado no existe"));

        // Reemplaza el/los rol(es) actuales por el nuevo rol seleccionado
        persona.getRoles().clear();
        persona.getRoles().add(rol);

        return personaRepository.save(persona);
    }
}