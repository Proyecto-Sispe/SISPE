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
    @Column(name = "id_insumo") private Long id;
    @Column(name = "nombre", nullable = false, unique = true) private String nombre;
    @Column(name = "stock_actual", nullable = false, precision = 12, scale = 3) private BigDecimal stockActual;
    @Column(name = "stock_minimo", nullable = false, precision = 12, scale = 3) private BigDecimal stockMinimo;
    @Column(name = "unidad", nullable = false) private String unidad;
    @Builder.Default @Column(name = "activo", nullable = false) private boolean activo = true;
}
