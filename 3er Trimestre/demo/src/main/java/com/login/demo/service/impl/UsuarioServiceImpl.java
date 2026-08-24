package com.login.demo.service.impl;

import com.login.demo.dto.UsuarioDTO;
import com.login.demo.mapper.UsuarioMapper;
import com.login.demo.model.Usuario;
import com.login.demo.repository.UsuarioRepository;
import com.login.demo.service.UsuarioService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class UsuarioServiceImpl implements UsuarioService {

    private final UsuarioRepository repository;
    private final UsuarioMapper mapper;

    public UsuarioServiceImpl(UsuarioRepository repository, UsuarioMapper mapper) {
        this.repository = repository;
        this.mapper = mapper;
    }

    @Override
    @Transactional(readOnly = true)
    public List<UsuarioDTO> listarTodos() {
        return repository.findAll().stream()
                .map(mapper::toDTO)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional
    public UsuarioDTO guardar(UsuarioDTO dto) {
        Usuario usuario = mapper.toEntity(dto);
        Usuario guardado = repository.save(usuario);
        return mapper.toDTO(guardado);
    }

    @Override
    @Transactional(readOnly = true)
    public UsuarioDTO obtenerPorId(Long id) {
        Usuario usuario = repository.findById(new com.login.demo.model.UsuarioId(id, 1))
                .orElseThrow(() -> new RuntimeException("Usuario no encontrado con id: " + id));
        return mapper.toDTO(usuario);
    }

    @Override
    @Transactional
    public void eliminar(Long id) {
        repository.deleteById(new com.login.demo.model.UsuarioId(id, 1));
    }
}
