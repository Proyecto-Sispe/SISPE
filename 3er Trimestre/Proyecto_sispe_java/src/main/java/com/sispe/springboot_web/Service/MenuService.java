package com.sispe.springboot_web.Service;

import com.sispe.springboot_web.Model.Menu;
import com.sispe.springboot_web.Repository.MenuRepository;
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