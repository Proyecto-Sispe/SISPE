package com.sispe.springboot_web.Controller;

import com.sispe.springboot_web.Model.Menu;
import com.sispe.springboot_web.Service.MenuService;
import com.sispe.springboot_web.Repository.CategoriaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
@RequiredArgsConstructor
public class MenuController {
    private final MenuService service;
    private final CategoriaRepository categorias;

    @GetMapping("/menu")
    public String index(Model model) {
        model.addAttribute("productos", service.listar());
        model.addAttribute("categorias", categorias.findAll());
        model.addAttribute("menu", new Menu());
        return "menu/index";
    }

    @GetMapping("/menu/digital")
    public String digital(Model model) {
        model.addAttribute("productos", service.listar());
        return "menu/digital";
    }

    @PostMapping("/menu/guardar")
    public String guardar(@ModelAttribute Menu menu, RedirectAttributes attributes) {
        if (menu.getCategoria() == null || menu.getCategoria().getId() == null || !categorias.existsById(menu.getCategoria().getId())) {
            attributes.addFlashAttribute("error", "Selecciona una categoría registrada en MySQL.");
            return "redirect:/menu";
        }
        service.guardar(menu);
        return "redirect:/menu";
    }

    @PostMapping("/menu/eliminar/{id}")
    public String eliminar(@PathVariable Integer id) { service.eliminar(id); return "redirect:/menu"; }

    @PostMapping("/menu/actualizar/{id}")
    public String actualizar(@PathVariable Integer id, @ModelAttribute Menu menu, RedirectAttributes attributes) {
        menu.setId(id);
        return guardar(menu, attributes);
    }
}