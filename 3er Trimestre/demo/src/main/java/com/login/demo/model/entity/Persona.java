package com.login.demo.model.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity @Table(name="Persona") @Getter @Setter @NoArgsConstructor
public class Persona {
 @EmbeddedId private PersonaId id;
 @Column(name="Nom1_usu") private String primerNombre;
 @Column(name="Nom2_usu") private String segundoNombre;
 @Column(name="Ape1_usu") private String primerApellido;
 @Column(name="Ape2_usu") private String segundoApellido;
 @Column(name="Telefono") private Long telefono;
 @Column(name="Correo_usu") private String correo;
 @Column(name="Password") private String password;
 private Boolean estado;
}
