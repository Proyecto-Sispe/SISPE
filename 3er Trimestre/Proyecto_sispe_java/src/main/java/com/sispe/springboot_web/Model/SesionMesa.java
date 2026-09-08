package com.sispe.springboot_web.Model;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "Sesion_Mesa")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class SesionMesa {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id_sesion") private Long id;
    @Column(name = "id_mesa", nullable = false) private Integer mesaId;
    @Column(name = "codigo_acceso", nullable = false) private String codigoAcceso;
    @Column(name = "nombre_cliente", nullable = false) private String nombreCliente;
    @Column(name = "cedula_cliente", nullable = false) private Integer cedulaCliente;
    @Column(name = "fecha_inicio") private LocalDateTime fechaInicio;
    @Column(name = "fecha_fin") private LocalDateTime fechaFin;
    private Boolean activa;
}