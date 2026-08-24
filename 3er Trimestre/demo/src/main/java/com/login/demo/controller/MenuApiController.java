package com.login.demo.controller;

import com.login.demo.model.Menu;
import com.login.demo.service.MenuService;
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
