package com.sispe.springboot_web.Service;

import com.sispe.springboot_web.Model.*;
import com.sispe.springboot_web.Repository.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal;
import java.util.*;

@Service
public class InventarioService {
    private final InsumoRepository insumos;
    private final MenuInsumoRepository recetas;
    private final DetallePedidoRepository detalles;

    public InventarioService(InsumoRepository insumos, MenuInsumoRepository recetas, DetallePedidoRepository detalles) {
        this.insumos = insumos; this.recetas = recetas; this.detalles = detalles;
    }

    /**
     * Descuenta una sola vez los insumos de un pedido entregado.
     * Las entidades y el mapa de consumos viven en el heap; las referencias locales y
     * parámetros pertenecen al marco de la llamada en el stack. Java administra ambos
     * espacios automáticamente, por eso se evita conservar referencias innecesarias.
     */
    @Transactional
    public void descontarPedido(Long pedidoId) {
        Map<Long, BigDecimal> consumo = new HashMap<>();
        for (DetallePedido detalle : detalles.findByPedidoId(pedidoId)) {
            for (MenuInsumo receta : recetas.findByMenu_Id(detalle.getMenu().getId())) {
                BigDecimal total = receta.getCantidad().multiply(BigDecimal.valueOf(detalle.getCantidad()));
                consumo.merge(receta.getInsumo().getId(), total, BigDecimal::add);
            }
        }
        Map<Long, Insumo> cargados = new HashMap<>();
        for (Map.Entry<Long, BigDecimal> entry : consumo.entrySet()) {
            Insumo insumo = insumos.findById(entry.getKey()).orElseThrow(() -> new IllegalStateException("Insumo no encontrado"));
            if (insumo.getStockActual().compareTo(entry.getValue()) < 0) {
                throw new IllegalStateException("Stock insuficiente para: " + insumo.getNombre());
            }
            cargados.put(entry.getKey(), insumo);
        }
        cargados.forEach((id, insumo) -> insumo.setStockActual(insumo.getStockActual().subtract(consumo.get(id))));
        insumos.saveAll(cargados.values());
    }

    @Transactional public Insumo guardar(Insumo insumo) { return insumos.save(insumo); }

    /**
     * Registra el ingrediente de una receta. Si ese insumo ya estaba asociado al
     * producto se actualiza su cantidad, en lugar de violar la restricción única
     * (id_menu, id_insumo) y devolver un error al usuario.
     */
    @Transactional public MenuInsumo guardarReceta(MenuInsumo receta) {
         return recetas.findByMenu_IdAndInsumo_Id(receta.getMenu().getId(), receta.getInsumo().getId())
                .map(existente -> { existente.setCantidad(receta.getCantidad()); return recetas.save(existente); })
                .orElseGet(() -> recetas.save(receta));
    }

    public Insumo buscar(Long insumoId) {
        return insumos.findById(insumoId).orElseThrow(() -> new IllegalArgumentException("Insumo no encontrado: " + insumoId));
    }

    public List<Insumo> listar() { return insumos.findByActivoTrueOrderByNombreAsc(); }
    public List<MenuInsumo> receta(Integer menuId) { return recetas.findByMenu_Id(menuId); }
    public List<MenuInsumo> recetas() { return recetas.findAll(); }
}
