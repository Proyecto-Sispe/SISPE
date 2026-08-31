package com.sispe.springboot_web.Controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;

import com.sispe.springboot_web.Model.Persona;
import com.sispe.springboot_web.Service.AuthService;

@Controller
public class AuthController {

    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    @GetMapping("/login")
    public String login() {
        return "login";
    }

    @GetMapping("/registro")
    public String mostrarRegistro(Model model) {
        model.addAttribute("persona", new Persona());
        return "registro";
    }

    @PostMapping("/registro")
    public String registrar(@ModelAttribute Persona persona, Model model) {
        try {
            // El servicio le asigna automáticamente el Rol Cliente (ID 4)
            authService.registrar(persona); 
            return "redirect:/login?registrado";
        } catch (IllegalArgumentException e) {
            model.addAttribute("error", e.getMessage());
            return "registro";
        }
    }
}