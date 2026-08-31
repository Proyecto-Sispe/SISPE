package com.sispe.springboot_web.Model;

import java.util.HashSet;
import java.util.Set;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.Id;
import jakarta.persistence.IdClass;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.JoinTable;
import jakarta.persistence.ManyToMany;
import jakarta.persistence.Table;

@Entity
@Table(name = "Persona")
@IdClass(PersonaId.class)
public class Persona {

    @Id
    @Column(name = "id_usuario")
    private Integer idUsuario;

    @Id
    @Column(name = "pkfk_Tipo_doc")
    private Integer tipoDocumento;

    @Column(name = "Nom1_usu")
    private String primerNombre;

    @Column(name = "Nom2_usu")
    private String segundoNombre;

    @Column(name = "Ape1_usu")
    private String primerApellido;

    @Column(name = "Ape2_usu")
    private String segundoApellido;

    @Column(name = "Telefono")
    private Long telefono;

    @Column(name = "Correo_usu")
    private String correo;

    @Column(name = "Password")
    private String password;

    @Column(name = "estado")
    private Integer estado;

    // Relación ManyToMany con la tabla Persona_has_Rol
    @ManyToMany(fetch = FetchType.EAGER)
    @JoinTable(
        name = "Persona_has_Rol",
        joinColumns = {
            @JoinColumn(name = "pkfk_id_usuario", referencedColumnName = "id_usuario"),
            @JoinColumn(name = "pkfk_Tipo_doc", referencedColumnName = "pkfk_Tipo_doc")
        },
        inverseJoinColumns = @JoinColumn(name = "pkfk_idRol", referencedColumnName = "idRol")
    )
    private Set<Rol> roles = new HashSet<>();

    public Persona() {}

    public Integer getIdUsuario() { return idUsuario; }
    public void setIdUsuario(Integer idUsuario) { this.idUsuario = idUsuario; }

    public Integer getTipoDocumento() { return tipoDocumento; }
    public void setTipoDocumento(Integer tipoDocumento) { this.tipoDocumento = tipoDocumento; }

    public String getPrimerNombre() { return primerNombre; }
    public void setPrimerNombre(String primerNombre) { this.primerNombre = primerNombre; }

    public String getSegundoNombre() { return segundoNombre; }
    public void setSegundoNombre(String segundoNombre) { this.segundoNombre = segundoNombre; }

    public String getPrimerApellido() { return primerApellido; }
    public void setPrimerApellido(String primerApellido) { this.primerApellido = primerApellido; }

    public String getSegundoApellido() { return segundoApellido; }
    public void setSegundoApellido(String segundoApellido) { this.segundoApellido = segundoApellido; }

    public Long getTelefono() { return telefono; }
    public void setTelefono(Long telefono) { this.telefono = telefono; }

    public String getCorreo() { return correo; }
    public void setCorreo(String correo) { this.correo = correo; }

    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }

    public Integer getEstado() { return estado; }
    public void setEstado(Integer estado) { this.estado = estado; }

    public Set<Rol> getRoles() { return roles; }
    public void setRoles(Set<Rol> roles) { this.roles = roles; }
}