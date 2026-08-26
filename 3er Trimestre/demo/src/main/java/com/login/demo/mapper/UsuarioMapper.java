package com.login.demo.mapper;

import com.login.demo.dto.UsuarioDTO;
import com.login.demo.model.Usuario;
import org.springframework.stereotype.Component;

@Component
public class UsuarioMapper {
    public UsuarioDTO toDTO(Usuario usuario) {
        if (usuario == null) return null;
        return new UsuarioDTO(usuario.getId(), usuario.getNombreCompleto(), usuario.getEmail(), null);
    }

    public Usuario toEntity(UsuarioDTO dto) {
        if (dto == null) return null;
        String[] partes = dto.getNombre().trim().split("\\s+", 2);
        return Usuario.builder()
                .id(dto.getId())
                .tipoDocumento(1)
                .primerNombre(partes[0])
                .primerApellido(partes.length > 1 ? partes[1] : partes[0])
                .email(dto.getEmail())
                .password("1234")
                .telefono(0L)
                .activo(true)
                .build();
    }
}
