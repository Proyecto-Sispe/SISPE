package com.sispe.springboot_web.repository;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;

import com.sispe.springboot_web.model.Persona;
import com.sispe.springboot_web.model.PersonaId;

public interface PersonaRepository extends JpaRepository<Persona, PersonaId> {

    Optional<Persona> findByCorreo(String correo);

    boolean existsByCorreo(String correo);
}