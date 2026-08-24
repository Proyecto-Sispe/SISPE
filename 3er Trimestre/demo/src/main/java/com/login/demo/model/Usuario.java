package com.login.demo.model;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "Persona")
@IdClass(UsuarioId.class)
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class Usuario {
    @Id @Column(name = "id_usuario") private Long id;
    @Id @Column(name = "pkfk_Tipo_doc") private Integer tipoDocumento;
    @Column(name = "Nom1_usu", nullable = false) private String primerNombre;
    @Column(name = "Nom2_usu") private String segundoNombre;
    @Column(name = "Ape1_usu", nullable = false) private String primerApellido;
    @Column(name = "Ape2_usu") private String segundoApellido;
    @Column(name = "Telefono", nullable = false) private Long telefono;
    @Column(name = "Correo_usu", unique = true) private String email;
    @Column(name = "Password", nullable = false) private String password;
    @Column(name = "estado") private Boolean activo;

    public String getNombreCompleto() {
        return (primerNombre + " " + primerApellido).trim();
    }
}
