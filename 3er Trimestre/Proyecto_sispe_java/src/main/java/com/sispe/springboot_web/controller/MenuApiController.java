package com.sispe.springboot_web.controller;

import com.sispe.springboot_web.model.Menu;
import com.sispe.springboot_web.service.MenuService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/menu")
@RequiredArgsConstructor
public class MenuApiController {
    private final MenuService service;
    @GetMapping public List<Menu> listar() { return service.listar(); }
    @PostMapping public Menu crear(@RequestBody Menu menu) { return service.guardar(menu); }
    @DeleteMapping("/{id}") public void eliminar(@PathVariable Integer id) { service.eliminar(id); }
}