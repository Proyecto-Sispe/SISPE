package com.login.demo.repository;

import com.login.demo.model.Usuario;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface UsuarioRepository extends JpaRepository<Usuario, com.login.demo.model.UsuarioId> {
    java.util.Optional<Usuario> findByEmailAndActivoTrue(String email);
}

