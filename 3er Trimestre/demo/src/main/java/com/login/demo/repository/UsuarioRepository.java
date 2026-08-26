package com.login.demo.repository;

import com.login.demo.model.Usuario;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface UsuarioRepository extends JpaRepository<Usuario, com.login.demo.model.UsuarioId> {
    java.util.Optional<Usuario> findByEmailAndActivoTrue(String email);

    @Query(value = "SELECT r.Nom_rol FROM Persona_has_Rol pr JOIN Rol r ON r.idRol = pr.pkfk_idRol WHERE pr.pkfk_id_usuario = :id AND pr.pkfk_Tipo_doc = :tipo", nativeQuery = true)
    List<String> findRoles(@Param("id") Long id, @Param("tipo") Integer tipo);
}

