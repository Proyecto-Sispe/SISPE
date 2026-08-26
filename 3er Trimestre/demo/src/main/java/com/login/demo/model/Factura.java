package com.login.demo.model;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "Factura")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class Factura {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id_factura") private Long id;
    @Column(name = "id_pedido", nullable = false) private Long pedidoId;
    @Column(name = "Fecha_hora") private LocalDateTime fechaHora;
    @Column(name = "Total", precision = 12, scale = 2) private BigDecimal total;
}
