package com.login.demo.model;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "Mesa")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class Mesa {
    @Id @Column(name = "id_Mesa") private Integer id;
    @Column(name = "Capacidad", nullable = false) private Integer capacidad;
    @Column(name = "Ubicacion", nullable = false) private String ubicacion;
    @Column(name = "Estado", nullable = false) private Boolean ocupada;
}
