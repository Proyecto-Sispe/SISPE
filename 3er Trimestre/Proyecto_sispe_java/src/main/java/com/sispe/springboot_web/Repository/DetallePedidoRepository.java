package com.sispe.springboot_web.Repository;

import com.sispe.springboot_web.Model.DetallePedido;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface DetallePedidoRepository extends JpaRepository<DetallePedido, Long> {
    List<DetallePedido> findByPedidoId(Long pedidoId);
    void deleteByPedidoId(Long pedidoId);
}