package com.sispe.springboot_web.repository;

import com.sispe.springboot_web.model.Pedido;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface PedidoRepository extends JpaRepository<Pedido, Long> {
    List<Pedido> findByEstadoInOrderByFechaPedidoAsc(List<String> estados);
}