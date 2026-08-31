package com.sispe.springboot_web.Controller;

import com.sispe.springboot_web.Model.Persona;
import com.sispe.springboot_web.Repository.PersonaRepository;
import com.sispe.springboot_web.Repository.RolRepository;
import com.sispe.springboot_web.Service.AuthService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;

@Controller
@RequestMapping("/admin")
@PreAuthorize("hasRole('ADMINISTRADOR')")
public class AdminController {

    private final AuthService authService;
    private final RolRepository rolRepository;
    private final PersonaRepository personaRepository;

    public AdminController(AuthService authService, RolRepository rolRepository, PersonaRepository personaRepository) {
        this.authService = authService;
        this.rolRepository = rolRepository;
        this.personaRepository = personaRepository;
    }

    // Formulario para crear un usuario con rol
    @GetMapping("/usuarios/nuevo")
    public String formularioNuevoPersona(Model model) {
        model.addAttribute("persona", new Persona());
        model.addAttribute("roles", rolRepository.findAll());
        return "admin/crear-usuario";
    }

    // Procesar la creación del usuario
    @PostMapping("/usuarios/nuevo")
    public String guardarPersonaConRol(@ModelAttribute Persona persona, @RequestParam("idRol") Integer idRol) {
        authService.registrarConRol(persona, idRol);
        return "redirect:/inicio?creado";
    }

    // Lista de todos los usuarios registrados, con su(s) rol(es) actual(es)
    @GetMapping("/usuarios")
    public String listarUsuarios(Model model) {
        model.addAttribute("usuarios", personaRepository.findAll());
        model.addAttribute("roles", rolRepository.findAll());
        return "admin/listar-usuarios";
    }

    // Cambiar el rol de un usuario existente (incluye convertirlo en Administrador)
    @PostMapping("/usuarios/cambiar-rol")
    public String cambiarRol(@RequestParam Integer idUsuario,
                              @RequestParam Integer tipoDocumento,
                              @RequestParam Integer idRol) {
        authService.cambiarRol(idUsuario, tipoDocumento, idRol);
        return "redirect:/admin/usuarios?actualizado";
    }
}