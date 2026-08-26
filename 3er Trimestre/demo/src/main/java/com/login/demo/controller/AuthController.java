package com.login.demo.controller;

import com.login.demo.model.Usuario;
import com.login.demo.repository.UsuarioRepository;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
public class AuthController {
    private final UsuarioRepository usuarios;
    private final org.springframework.security.crypto.password.PasswordEncoder encoder;
    public AuthController(UsuarioRepository usuarios, org.springframework.security.crypto.password.PasswordEncoder encoder) {
        this.usuarios = usuarios;
        this.encoder = encoder;
    }

    @GetMapping({"/", "/login"})
    public String login() { return "login"; }

    @PostMapping("/login")
    public String autenticar(@RequestParam String email, @RequestParam String password,
                             HttpSession session, Model model) {
        Usuario usuario = usuarios.findByEmailAndActivoTrue(email.trim()).orElse(null);
        if (usuario != null && (password.equals(usuario.getPassword()) || encoder.matches(password, usuario.getPassword()))) {
            session.setAttribute("usuario", usuario);
            session.setAttribute("rol", rolDe(usuario));
            return "redirect:/dashboard";
        }
        model.addAttribute("error", "Correo o contraseña incorrectos.");
        return "login";
    }

    private String rolDe(Usuario usuario) {
        return switch (usuario.getTipoDocumento()) {
            case 1 -> "ADMIN";
            case 2 -> "COCINA";
            case 3 -> "CAJERO";
            default -> "CLIENTE";
        };
    }

    @GetMapping("/logout")
    public String salir(HttpSession session) { session.invalidate(); return "redirect:/login"; }

    @GetMapping("/dashboard")
    public String dashboard(HttpSession session) {
        return session.getAttribute("usuario") == null ? "redirect:/login" : "dashboard";
    }
}
