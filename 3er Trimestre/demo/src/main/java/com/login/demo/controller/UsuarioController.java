package com.login.demo.controller;

import com.login.demo.dto.UsuarioDTO;
import com.login.demo.service.UsuarioService;
import jakarta.validation.Valid;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;

@Controller
@RequestMapping("/usuarios")
public class UsuarioController {

    private final UsuarioService usuarioService;

    public UsuarioController(UsuarioService usuarioService) {
        this.usuarioService = usuarioService;
    }

    // Listar usuarios en Thymeleaf
    @GetMapping
    public String listar(Model model) {
        model.addAttribute("usuarios", usuarioService.listarTodos());
        return "usuarios/lista"; // Redirige a src/main/resources/templates/usuarios/lista.html
    }

    // Formulario de creación
    @GetMapping("/nuevo")
    public String formularioNuevo(@RequestParam(required = false) Long id, Model model) {
        model.addAttribute("usuario", new UsuarioDTO());
        model.addAttribute("modoEdicion", id != null);
        return "usuarios/nuevo";
    }

    // Guardar con validaciones [JER-02]
    @PostMapping("/guardar")
    public String guardar(@Valid @ModelAttribute("usuario") UsuarioDTO dto, 
                        BindingResult result, 
                        Model model) {
        if (result.hasErrors()) {
            return "usuarios/nuevo"; // Si hay error, recarga la vista con las alertas
        }
        usuarioService.guardar(dto);
        return "redirect:/usuarios";
    }

    // Eliminar registro
    @PostMapping("/actualizar/{id}")
    public String actualizar(@PathVariable Long id, @Valid @ModelAttribute("usuario") UsuarioDTO dto, BindingResult result) {
        if (result.hasErrors()) return "usuarios/nuevo";
        dto.setId(id);
        usuarioService.guardar(dto);
        return "redirect:/usuarios";
    }

    @PostMapping("/eliminar/{id}")
    public String eliminar(@PathVariable Long id) { usuarioService.eliminar(id); return "redirect:/usuarios"; }

    @GetMapping("/eliminar/{id}")
    public String eliminarCompatibilidad(@PathVariable Long id) { return eliminar(id); }
}
