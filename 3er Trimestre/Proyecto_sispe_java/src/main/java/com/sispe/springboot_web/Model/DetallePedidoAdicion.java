package com.sispe.springboot_web.Model;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "Detalle_Pedido_Adicion")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class DetallePedidoAdicion {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id") private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "id_detalle", nullable = false)
    private DetallePedido detallePedido;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "id_adicion", nullable = false)
    private Adicion adicion;

    @Builder.Default @Column(name = "cantidad", nullable = false) private Integer cantidad = 1;
}