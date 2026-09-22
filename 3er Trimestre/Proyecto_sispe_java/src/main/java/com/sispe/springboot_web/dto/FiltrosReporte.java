package com.sispe.springboot_web.dto;

import java.time.LocalDate;

import org.springframework.format.annotation.DateTimeFormat;

/**
 * Criterios del reporte multitabla. Todos son opcionales y se combinan con AND.
 * Los nombres de los campos coinciden con los parámetros del formulario de la pantalla.
 */
public class FiltrosReporte {
    @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
    private LocalDate desde;
    @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
    private LocalDate hasta;
    private String estado;
    private String prioridad;
    private Long mesa;
    private Integer categoria;
    private Integer producto;
    private Integer metodoPago;

    public LocalDate getDesde() { return desde; }
    public void setDesde(LocalDate desde) { this.desde = desde; }
    public LocalDate getHasta() { return hasta; }
    public void setHasta(LocalDate hasta) { this.hasta = hasta; }
    public String getEstado() { return estado; }
    public void setEstado(String estado) { this.estado = estado; }
    public String getPrioridad() { return prioridad; }
    public void setPrioridad(String prioridad) { this.prioridad = prioridad; }
    public Long getMesa() { return mesa; }
    public void setMesa(Long mesa) { this.mesa = mesa; }
    public Integer getCategoria() { return categoria; }
    public void setCategoria(Integer categoria) { this.categoria = categoria; }
    public Integer getProducto() { return producto; }
    public void setProducto(Integer producto) { this.producto = producto; }
    public Integer getMetodoPago() { return metodoPago; }
    public void setMetodoPago(Integer metodoPago) { this.metodoPago = metodoPago; }

    /** Devuelve el problema del rango de fechas, o null si los criterios son coherentes. */
    public String problema() {
        if (desde != null && hasta != null && hasta.isBefore(desde)) {
            return "La fecha «Hasta» no puede ser anterior a «Desde». Corrige el rango para ver resultados.";
        }
        return null;
    }
}
