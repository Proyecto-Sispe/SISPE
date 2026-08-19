package com.login.demo.model.entity;
import jakarta.persistence.*; import lombok.*; import java.time.LocalDateTime;
@Entity @Table(name="Pedido") @Getter @Setter @NoArgsConstructor
public class Pedido { @Id @GeneratedValue(strategy=GenerationType.IDENTITY) @Column(name="id_pedido") private Integer id; @Column(name="id_mesa") private Integer mesaId; @Column(name="id_sesion_qr") private Integer sesionQrId; private LocalDateTime fechaPedido; @Enumerated(EnumType.STRING) private EstadoPedido estado; @Enumerated(EnumType.STRING) private Prioridad prioridad; private Integer tiempoEstimado; private String observaciones; public enum EstadoPedido { pendiente,en_preparacion,en_camino,entregado } public enum Prioridad { normal,urgente } }
