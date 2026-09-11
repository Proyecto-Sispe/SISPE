package com.sispe.springboot_web.Model;

import jakarta.persistence.Embeddable;
import lombok.*;
import java.io.Serializable;

@Embeddable
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @EqualsAndHashCode
public class FacturaMetodoPagoId implements Serializable {
    private Long facturaId;
    private Integer metodoPagoId;
}