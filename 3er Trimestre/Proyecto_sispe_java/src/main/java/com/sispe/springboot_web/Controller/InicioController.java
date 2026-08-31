package com.sispe.springboot_web.Controller;

import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import com.sispe.springboot_web.Model.Persona;
import com.sispe.springboot_web.Repository.PersonaRepository;

@Controller
public class InicioController {

    private final PersonaRepository personaRepository;

    public InicioController(PersonaRepository personaRepository) {
        this.personaRepository = personaRepository;
    }

    @GetMapping("/acceso-denegado")
    public String accesoDenegado() {
        return "acceso-denegado";
    }

    @GetMapping("/inicio")
    public String inicio(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        if (userDetails != null) {
            Persona persona = personaRepository.findByCorreo(userDetails.getUsername())
                    .orElse(null);
            model.addAttribute("persona", persona);
        }

        return "inicio";
    }
}