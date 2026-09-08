package com.sispe.springboot_web.Controller;

import com.sispe.springboot_web.Model.Persona;
import com.sispe.springboot_web.Repository.PersonaRepository;
import com.sispe.springboot_web.Repository.RolRepository;
import com.sispe.springboot_web.Service.AuthService;
import com.sispe.springboot_web.dto.PersonaDTO;
import com.sispe.springboot_web.mapper.PersonaMapper;
import jakarta.validation.Valid;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;

@Controller
@RequestMapping("/admin")
@PreAuthorize("hasRole('ADMINISTRADOR')")
public class AdminController {

    private final AuthService authService;
    private final RolRepository rolRepository;
    private final PersonaRepository personaRepository;
    private final PersonaMapper personaMapper;

    public AdminController(AuthService authService, RolRepository rolRepository,
                            PersonaRepository personaRepository, PersonaMapper personaMapper) {
        this.authService = authService;
        this.rolRepository = rolRepository;
        this.personaRepository = personaRepository;
        this.personaMapper = personaMapper;
    }

    @GetMapping("/usuarios/nuevo")
    public String formularioNuevoPersona(Model model) {
        model.addAttribute("personaDTO", new PersonaDTO());
        model.addAttribute("roles", rolRepository.findAll());
        return "admin/crear-usuario";
    }

    @PostMapping("/usuarios/nuevo")
    public String guardarPersonaConRol(@Valid @ModelAttribute("personaDTO") PersonaDTO dto,
                                        BindingResult result, @RequestParam("idRol") Integer idRol,
                                        Model model) {
        if (result.hasErrors()) {
            model.addAttribute("roles", rolRepository.findAll());
            return "admin/crear-usuario";
        }
        Persona persona = personaMapper.toEntity(dto);
        authService.registrarConRol(persona, idRol);
        return "redirect:/inicio?creado";
    }

    @GetMapping("/usuarios")
    public String listarUsuarios(Model model) {
        model.addAttribute("usuarios", personaRepository.findAll());
        model.addAttribute("roles", rolRepository.findAll());
        return "admin/listar-usuarios";
    }

    @PostMapping("/usuarios/cambiar-rol")
    public String cambiarRol(@RequestParam Integer idUsuario,
                              @RequestParam Integer tipoDocumento,
                              @RequestParam Integer idRol) {
        authService.cambiarRol(idUsuario, tipoDocumento, idRol);
        return "redirect:/admin/usuarios?actualizado";
    }
}