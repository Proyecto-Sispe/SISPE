package com.sispe.springboot_web.Repository;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;

import com.sispe.springboot_web.Model.Persona;
import com.sispe.springboot_web.Model.PersonaId;

public interface PersonaRepository extends JpaRepository<Persona, PersonaId> {

    Optional<Persona> findByCorreo(String correo);

    boolean existsByCorreo(String correo);
}