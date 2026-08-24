package com.login.demo.controller;

import com.login.demo.model.Menu;
import com.login.demo.service.MenuService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
@RequiredArgsConstructor
public class MenuController {
    private final MenuService service;
    @GetMapping({"/", "/menu", "/gestion-menu"})
    public String index(Model model) { model.addAttribute("productos", service.listar()); return "menu/index"; }
    @PostMapping("/menu/guardar")
    public String guardar(@ModelAttribute Menu menu) { service.guardar(menu); return "redirect:/menu"; }
    @PostMapping("/menu/eliminar/{id}")
    public String eliminar(@PathVariable Integer id) { service.eliminar(id); return "redirect:/menu"; }
}
