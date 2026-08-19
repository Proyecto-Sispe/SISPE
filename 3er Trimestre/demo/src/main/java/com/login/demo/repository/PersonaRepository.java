package com.login.demo.repository;
import com.login.demo.model.entity.*; import org.springframework.data.jpa.repository.JpaRepository; import java.util.*;
public interface PersonaRepository extends JpaRepository<Persona, PersonaId> { Optional<Persona> findByCorreo(String correo); List<Persona> findAllByOrderByPrimerNombreAsc(); }
