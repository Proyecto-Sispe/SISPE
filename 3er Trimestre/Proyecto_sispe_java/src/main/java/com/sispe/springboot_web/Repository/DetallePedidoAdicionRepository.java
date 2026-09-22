package com.sispe.springboot_web.Repository;
import com.sispe.springboot_web.Model.DetallePedidoAdicion;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

public interface DetallePedidoAdicionRepository extends JpaRepository<DetallePedidoAdicion, Long> {
    List<DetallePedidoAdicion> findByDetallePedido_Id(Long detalleId);
    @Transactional
    void deleteByDetallePedido_Id(Long detalleId);
}