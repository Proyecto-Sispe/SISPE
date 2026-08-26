package com.login.demo.service;

import com.login.demo.model.Menu;
import com.login.demo.repository.MenuRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
@RequiredArgsConstructor
public class MenuService {
    private final MenuRepository repository;
    public List<Menu> listar() { return repository.findAll(); }
    public Menu guardar(Menu menu) { return repository.save(menu); }
    public void eliminar(Integer id) { repository.deleteById(id); }
}
