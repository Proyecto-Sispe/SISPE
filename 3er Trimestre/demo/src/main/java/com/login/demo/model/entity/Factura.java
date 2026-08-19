package com.login.demo.model.entity;
import jakarta.persistence.*; import lombok.*; import java.time.LocalDateTime;
@Entity @Table(name="Factura") @Getter @Setter @NoArgsConstructor
public class Factura { @Id @GeneratedValue(strategy=GenerationType.IDENTITY) @Column(name="id_factura") private Integer id; @Column(name="id_pedido") private Integer pedidoId; @Column(name="Fecha_hora") private LocalDateTime fechaHora; @Column(name="Total") private Double total; }
