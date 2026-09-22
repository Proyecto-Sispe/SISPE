package com.sispe.springboot_web.Repository;

import com.sispe.springboot_web.Model.DetallePedido;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

public interface DetallePedidoRepository extends JpaRepository<DetallePedido, Long> {
    List<DetallePedido> findByPedidoId(Long pedidoId);
    @Transactional
    void deleteByPedidoId(Long pedidoId);
}