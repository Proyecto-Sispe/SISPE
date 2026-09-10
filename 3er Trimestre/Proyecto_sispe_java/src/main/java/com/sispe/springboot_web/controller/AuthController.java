package com.sispe.springboot_web.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;

import com.sispe.springboot_web.model.Persona;
import com.sispe.springboot_web.service.AuthService;

@Controller
public class AuthController {

    // La referencia authService pertenece al objeto AuthController, que vive en el heap.
    // El valor de la referencia se mantiene como parte del estado del controlador.
    private final AuthService authService;

    public AuthController(AuthService authService) {
        // authService es una referencia local almacenada temporalmente en el stack.
        // El objeto AuthService al que apunta es administrado en el heap por Spring.
        this.authService = authService;
    }

    @GetMapping("/login")
    public String login() {
        return "login";
    }

    @GetMapping("/registro")
    public String mostrarRegistro(Model model) {
        // model es una referencia de parámetro ubicada en el stack durante esta llamada.
        // El objeto Model es gestionado por Spring en el heap.
        // new Persona() crea el objeto Persona en el heap; la referencia temporal se usa aquí.
        model.addAttribute("persona", new Persona());
        return "registro";
    }

    @PostMapping("/registro")
    public String registrar(@ModelAttribute Persona persona, Model model) {
        // persona y model son referencias de parámetros almacenadas temporalmente en el stack.
        // Los objetos Persona y Model referenciados viven en el heap y son gestionados por Spring.
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