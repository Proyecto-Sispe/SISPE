package com.sispe.springboot_web.model;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;

@Entity
@Table(name = "Detalle_Pedido")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class DetallePedido {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id_detalle") private Long id;
    @Column(name = "id_pedido", nullable = false) private Long pedidoId;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "id_menu", nullable = false)
    private Menu menu;

    @Column(name = "cantidad", nullable = false) private Integer cantidad;
    @Column(name = "valor_venta", nullable = false) private BigDecimal valorVenta;
    private String observaciones;
}