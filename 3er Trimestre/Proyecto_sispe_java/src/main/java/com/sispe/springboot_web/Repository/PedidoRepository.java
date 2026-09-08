package com.sispe.springboot_web.Repository;

import com.sispe.springboot_web.Model.Pedido;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface PedidoRepository extends JpaRepository<Pedido, Long> {
    List<Pedido> findByEstadoInOrderByFechaPedidoAsc(List<String> estados);
}