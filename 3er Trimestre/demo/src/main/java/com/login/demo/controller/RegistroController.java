package com.login.demo.controller;

import com.login.demo.model.Usuario;
import com.login.demo.repository.UsuarioRepository;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

@Controller
@Validated
public class RegistroController {
    private final UsuarioRepository usuarios;
    private final PasswordEncoder encoder;

    public RegistroController(UsuarioRepository usuarios, PasswordEncoder encoder) {
        this.usuarios = usuarios;
        this.encoder = encoder;
    }

    @GetMapping("/registro")
    public String formulario() { return "registro"; }

    @PostMapping("/registro")
    public String registrar(@RequestParam @NotNull Long idUsuario, @RequestParam(defaultValue = "1") Integer tipoDocumento,
                            @RequestParam @NotBlank String nombre, @RequestParam @NotBlank String apellido,
                            @RequestParam Long telefono, @RequestParam @Email String email,
                            @RequestParam @NotBlank String password, Model model) {
        if (usuarios.findByEmailAndActivoTrue(email.trim()).isPresent()) {
            model.addAttribute("error", "El correo ya está registrado.");
            return "registro";
        }
        Usuario usuario = Usuario.builder().id(idUsuario).tipoDocumento(tipoDocumento).primerNombre(nombre.trim())
                .primerApellido(apellido.trim()).telefono(telefono).email(email.trim()).password(encoder.encode(password))
                .activo(true).build();
        usuarios.save(usuario);
        return "redirect:/login?registrado";
    }
}
