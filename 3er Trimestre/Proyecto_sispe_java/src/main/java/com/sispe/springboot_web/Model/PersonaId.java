package com.sispe.springboot_web.Model;

import java.io.Serializable;
import java.util.Objects;

public class PersonaId implements Serializable {

    private Integer idUsuario;
    private Integer tipoDocumento;

    public PersonaId() {
    }

    public PersonaId(Integer idUsuario, Integer tipoDocumento) {
        this.idUsuario = idUsuario;
        this.tipoDocumento = tipoDocumento;
    }

    public Integer getIdUsuario() {
        return idUsuario;
    }

    public void setIdUsuario(Integer idUsuario) {
        this.idUsuario = idUsuario;
    }

    public Integer getTipoDocumento() {
        return tipoDocumento;
    }

    public void setTipoDocumento(Integer tipoDocumento) {
        this.tipoDocumento = tipoDocumento;
    }

    @Override
    public boolean equals(Object o) {

        if (this == o) {
            return true;
        }

        if (o == null || getClass() != o.getClass()) {
            return false;
        }

        PersonaId personaId = (PersonaId) o;

        return Objects.equals(idUsuario, personaId.idUsuario)
                && Objects.equals(tipoDocumento, personaId.tipoDocumento);
    }

    @Override
    public int hashCode() {
        return Objects.hash(idUsuario, tipoDocumento);
    }
}