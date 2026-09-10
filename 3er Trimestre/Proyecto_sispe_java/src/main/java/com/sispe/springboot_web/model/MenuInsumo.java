package com.sispe.springboot_web.model;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;

/** Relación de receta: cantidad de un insumo necesaria para una unidad del menú. */
@Entity
@Table(name = "Menu_Insumo", uniqueConstraints = @UniqueConstraint(columnNames = {"id_menu", "id_insumo"}))
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class MenuInsumo {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id_menu_insumo") private Long id;
    @ManyToOne(fetch = FetchType.EAGER, optional = false) @JoinColumn(name = "id_menu") private Menu menu;
    @ManyToOne(fetch = FetchType.EAGER, optional = false) @JoinColumn(name = "id_insumo") private Insumo insumo;
    @Column(name = "cantidad", nullable = false, precision = 12, scale = 3) private BigDecimal cantidad;
}
