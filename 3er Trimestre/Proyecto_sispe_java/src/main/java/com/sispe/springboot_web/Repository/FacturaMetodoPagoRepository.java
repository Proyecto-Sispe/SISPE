package com.sispe.springboot_web.Repository;
import com.sispe.springboot_web.Model.FacturaMetodoPago;
import com.sispe.springboot_web.Model.FacturaMetodoPagoId;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface FacturaMetodoPagoRepository extends JpaRepository<FacturaMetodoPago, FacturaMetodoPagoId> {
    Optional<FacturaMetodoPago> findByFactura_Id(Long facturaId);
}