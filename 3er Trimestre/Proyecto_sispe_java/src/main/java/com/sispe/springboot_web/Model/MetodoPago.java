package com.sispe.springboot_web.Model;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "Metodo_pago")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class MetodoPago {
    @Id @Column(name = "id_pago") private Integer id;
    @Column(name = "Tipo_pago", nullable = false) private String tipo;
}