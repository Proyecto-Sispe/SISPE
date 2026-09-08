package com.sispe.springboot_web.dto;

import jakarta.validation.constraints.*;

public class PersonaDTO {

    private Integer idUsuario;

    @NotNull(message = "El tipo de documento es obligatorio")
    private Integer tipoDocumento;

    @NotBlank(message = "El primer nombre es obligatorio")
    @Size(min = 2, max = 20, message = "El nombre debe tener entre 2 y 20 caracteres")
    private String primerNombre;

    private String segundoNombre;

    @NotBlank(message = "El primer apellido es obligatorio")
    @Size(min = 2, max = 20, message = "El apellido debe tener entre 2 y 20 caracteres")
    private String primerApellido;

    private String segundoApellido;

    @NotNull(message = "El teléfono es obligatorio")
    private Long telefono;

    @NotBlank(message = "El correo no puede estar vacío")
    @Email(message = "Debe ser un correo electrónico válido")
    private String correo;

    @NotBlank(message = "La contraseña es obligatoria")
    @Size(min = 4, message = "La contraseña debe tener al menos 4 caracteres")
    private String password;

    // Constructores
    public PersonaDTO() {}

    // Getters y Setters
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
}