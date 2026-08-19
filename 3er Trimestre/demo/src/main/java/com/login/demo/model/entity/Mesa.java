package com.login.demo.model.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity @Table(name="Mesa") @Getter @Setter @NoArgsConstructor
public class Mesa { @Id @Column(name="id_Mesa") private Integer id; @Column(name="Capacidad") private Integer capacidad; @Column(name="Ubicacion") private String ubicacion; @Column(name="Estado") private Boolean estado; }
