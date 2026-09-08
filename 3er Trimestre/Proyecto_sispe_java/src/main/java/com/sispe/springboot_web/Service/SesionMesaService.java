package com.sispe.springboot_web.Service;

import org.springframework.jdbc.core.SqlOutParameter;
import org.springframework.jdbc.core.SqlParameter;
import org.springframework.jdbc.core.simple.SimpleJdbcCall;
import org.springframework.stereotype.Service;

import javax.sql.DataSource;
import java.sql.Types;
import java.util.Map;

@Service
public class SesionMesaService {
    private final SimpleJdbcCall registrarClienteCall;
    private final SimpleJdbcCall despacharPedidoCall;

    public SesionMesaService(DataSource dataSource) {
        this.registrarClienteCall = new SimpleJdbcCall(dataSource)
                .withProcedureName("RegistrarClienteYCrearPedido")
                .declareParameters(
                        new SqlParameter("p_id_mesa", Types.INTEGER),
                        new SqlParameter("p_nombre", Types.VARCHAR),
                        new SqlParameter("p_cedula", Types.INTEGER),
                        new SqlOutParameter("p_id_pedido_nuevo", Types.INTEGER)
                );
        this.despacharPedidoCall = new SimpleJdbcCall(dataSource)
                .withProcedureName("DespacharPedidoYLiberarMesa")
                .declareParameters(new SqlParameter("p_id_pedido", Types.INTEGER));
    }

    public Long registrarClienteYCrearPedido(Integer idMesa, String nombre, Integer cedula) {
        Map<String, Object> resultado = registrarClienteCall.execute(
                Map.of("p_id_mesa", idMesa, "p_nombre", nombre, "p_cedula", cedula));
        return ((Number) resultado.get("p_id_pedido_nuevo")).longValue();
    }

    public void despacharPedido(Long idPedido) {
        despacharPedidoCall.execute(Map.of("p_id_pedido", idPedido));
    }
}