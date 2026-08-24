package com.login.demo.model;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "Pedido")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class Pedido {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id_pedido")
    private Long id;
    @Column(name = "id_mesa") private Long mesaId;
    @Column(name = "mesero_tipo_doc") private Integer meseroTipoDocumento;
    @Column(name = "mesero_id_usuario") private Long meseroId;
    @Column(name = "cliente_tipo_doc") private Integer clienteTipoDocumento;
    @Column(name = "cliente_id_usuario") private Long clienteId;
    @Column(name = "id_sesion_qr") private Long sesionQrId;
    @Column(name = "fecha_pedido") private LocalDateTime fechaPedido;
    private String estado;
    private String prioridad;
    @Column(name = "cocinero_asignado") private Long cocineroAsignado;
    @Column(name = "tiempo_estimado") private Integer tiempoEstimado;
    private String observaciones;
}
