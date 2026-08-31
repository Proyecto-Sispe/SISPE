package com.sispe.springboot_web.Model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "Rol")
public class Rol {

    @Id
    @Column(name = "idRol")
    private Integer idRol;

    @Column(name = "Nom_rol", nullable = false, length = 45)
    private String nombre;

    public Rol() {}

    public Integer getIdRol() { return idRol; }
    public void setIdRol(Integer idRol) { this.idRol = idRol; }

    public String getNombre() { return nombre; }
    public void setNombre(String nombre) { this.nombre = nombre; }
}