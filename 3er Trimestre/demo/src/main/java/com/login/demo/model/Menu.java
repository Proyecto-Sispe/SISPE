package com.login.demo.model;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;

@Entity
@Table(name = "Menu")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class Menu {
    @Id @Column(name = "id_menu") private Integer id;
    @Column(name = "Productos", nullable = false) private String producto;
    @Column(name = "Precio", nullable = false, precision = 12, scale = 2) private BigDecimal precio;
    @Column(name = "descripcion", nullable = false) private String descripcion;
    @ManyToOne(fetch = FetchType.LAZY) @JoinColumn(name = "pkfk_id_categoria", nullable = false) private Categoria categoria;
}
