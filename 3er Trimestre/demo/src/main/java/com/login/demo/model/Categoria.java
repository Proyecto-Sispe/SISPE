package com.login.demo.model;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "Categoria")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class Categoria {
    @Id @Column(name = "id_categoria") private Integer id;
    @Column(name = "nom_categoria", nullable = false) private String nombre;
}
