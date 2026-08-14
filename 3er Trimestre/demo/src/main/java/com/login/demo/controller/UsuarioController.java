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
    public String formularioNuevo(Model model) {
        model.addAttribute("usuario", new UsuarioDTO());
        return "usuarios/formulario";
    }

    // Guardar con validaciones [JER-02]
    @PostMapping("/guardar")
    public String guardar(@Valid @ModelAttribute("usuario") UsuarioDTO dto, 
                        BindingResult result, 
                        Model model) {
        if (result.hasErrors()) {
            return "usuarios/formulario"; // Si hay error, recarga la vista con las alertas
        }
        usuarioService.guardar(dto);
        return "redirect:/usuarios";
    }

    // Eliminar registro
    @GetMapping("/eliminar/{id}")
    public String eliminar(@PathVariable Long id) {
        usuarioService.eliminar(id);
        return "redirect:/usuarios";
    }
}
