package com.sispe.springboot_web.Model;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;

@Entity
@Table(name = "Adicion")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class Adicion {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id_adicion") private Long id;
    @Column(name = "nombre", nullable = false) private String nombre;
    @Column(name = "precio", nullable = false, precision = 10, scale = 2) private BigDecimal precio;
}