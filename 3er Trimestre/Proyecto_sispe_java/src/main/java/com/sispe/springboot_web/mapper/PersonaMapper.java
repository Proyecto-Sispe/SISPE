package com.sispe.springboot_web.mapper;

import com.sispe.springboot_web.model.Persona;
import com.sispe.springboot_web.dto.PersonaDTO;
import org.springframework.stereotype.Component;

@Component
public class PersonaMapper {

    public PersonaDTO toDTO(Persona persona) {
        if (persona == null) return null;
        PersonaDTO dto = new PersonaDTO();
        dto.setIdUsuario(persona.getIdUsuario());
        dto.setTipoDocumento(persona.getTipoDocumento());
        dto.setPrimerNombre(persona.getPrimerNombre());
        dto.setSegundoNombre(persona.getSegundoNombre());
        dto.setPrimerApellido(persona.getPrimerApellido());
        dto.setSegundoApellido(persona.getSegundoApellido());
        dto.setTelefono(persona.getTelefono());
        dto.setCorreo(persona.getCorreo());
        dto.setPassword(""); // nunca se devuelve la contraseña real al formulario
        return dto;
    }

    public Persona toEntity(PersonaDTO dto) {
        if (dto == null) return null;
        Persona persona = new Persona();
        persona.setIdUsuario(dto.getIdUsuario());
        persona.setTipoDocumento(dto.getTipoDocumento());
        persona.setPrimerNombre(dto.getPrimerNombre());
        persona.setSegundoNombre(dto.getSegundoNombre());
        persona.setPrimerApellido(dto.getPrimerApellido());
        persona.setSegundoApellido(dto.getSegundoApellido());
        persona.setTelefono(dto.getTelefono());
        persona.setCorreo(dto.getCorreo());
        persona.setPassword(dto.getPassword());
        return persona;
    }
}