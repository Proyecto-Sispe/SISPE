package com.login.demo.mapper;

import com.login.demo.dto.UsuarioDTO;
import com.login.demo.model.Usuario;
import org.springframework.stereotype.Component;

@Component
public class UsuarioMapper {

    // Entidad a DTO
    public UsuarioDTO toDTO(Usuario usuario) {
        if (usuario == null) return null;
        return UsuarioDTO.builder()
                .id(usuario.getId())
                .nombre(usuario.getNombre())
                .email(usuario.getEmail())
                .edad(usuario.getEdad())
                .build();
    }

    // DTO a Entidad
    public Usuario toEntity(UsuarioDTO dto) {
        if (dto == null) return null;
        return Usuario.builder()
                .id(dto.getId())
                .nombre(dto.getNombre())
                .email(dto.getEmail())
                .edad(dto.getEdad())
                .build();
    }
}