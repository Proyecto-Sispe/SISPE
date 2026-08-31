package com.sispe.springboot_web.Controller;

import com.sispe.springboot_web.Service.PasswordResetService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

@Controller
@RequestMapping("/login")
public class PasswordResetController {

    private final PasswordResetService resetService;

    public PasswordResetController(PasswordResetService resetService) {
        this.resetService = resetService;
    }

    @GetMapping("/olvide")
    public String formularioOlvide() {
        return "olvide-password";
    }

    @PostMapping("/olvide")
    public String enviarCodigo(@RequestParam String correo, RedirectAttributes attributes) {
        resetService.solicitarCodigo(correo);
        attributes.addFlashAttribute("mensaje",
                "Si el correo está registrado, te enviamos un código de verificación.");
        attributes.addAttribute("correo", correo);
        return "redirect:/login/verificar";
    }

    @GetMapping("/verificar")
    public String formularioVerificar(@RequestParam(required = false) String correo, Model model) {
        model.addAttribute("correo", correo);
        return "verificar-codigo";
    }

    @PostMapping("/verificar")
    public String restablecer(@RequestParam String correo,
                               @RequestParam String codigo,
                               @RequestParam String nuevaPassword,
                               Model model) {
        try {
            resetService.restablecerPassword(correo, codigo, nuevaPassword);
            return "redirect:/login?recuperado";
        } catch (IllegalArgumentException e) {
            model.addAttribute("error", e.getMessage());
            model.addAttribute("correo", correo);
            return "verificar-codigo";
        }
    }
}