package com.login.demo.service;

import com.login.demo.dto.UsuarioDTO;
import java.util.List;

public interface UsuarioService {
    List<UsuarioDTO> listarTodos();
    UsuarioDTO guardar(UsuarioDTO dto);
    UsuarioDTO obtenerPorId(Long id);
    void eliminar(Long id);
}
