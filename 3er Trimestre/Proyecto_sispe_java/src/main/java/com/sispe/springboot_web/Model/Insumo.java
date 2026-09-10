package com.sispe.springboot_web.Model;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;

/** Insumo reutilizable que compone uno o varios productos del menú. */
@Entity
@Table(name = "Insumo")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class Insumo {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(nullable = false, unique = true) private String nombre;
    @Column(nullable = false, precision = 12, scale = 3) private BigDecimal stockActual;
    @Column(nullable = false, precision = 12, scale = 3) private BigDecimal stockMinimo;
    @Column(nullable = false) private String unidad;
    @Column(nullable = false) private boolean activo = true;
}
