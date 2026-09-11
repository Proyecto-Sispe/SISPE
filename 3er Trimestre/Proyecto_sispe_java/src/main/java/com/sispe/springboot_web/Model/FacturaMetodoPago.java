package com.sispe.springboot_web.Model;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;

@Entity
@Table(name = "Factura_has_Metodo_pago")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class FacturaMetodoPago {
    @EmbeddedId private FacturaMetodoPagoId id;

    @ManyToOne(fetch = FetchType.LAZY)
    @MapsId("facturaId")
    @JoinColumn(name = "pkfk_n_factura")
    private Factura factura;

    @ManyToOne(fetch = FetchType.EAGER)
    @MapsId("metodoPagoId")
    @JoinColumn(name = "pkfk_metodo_pago")
    private MetodoPago metodoPago;

    @Column(name = "monto", nullable = false) private BigDecimal monto;
}