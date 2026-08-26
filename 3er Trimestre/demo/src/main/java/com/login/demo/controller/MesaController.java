package com.login.demo.controller;

import com.login.demo.model.Mesa;
import com.login.demo.repository.MesaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
@RequiredArgsConstructor
public class MesaController {
    private final MesaRepository repository;
    @GetMapping("/mesas")
    public String index(Model model) { model.addAttribute("mesas", repository.findAll()); return "mesas/index"; }
    @PostMapping("/mesas/guardar")
    public String guardar(@ModelAttribute Mesa mesa) { repository.save(mesa); return "redirect:/mesas"; }
    @PostMapping("/mesas/eliminar/{id}")
    public String eliminar(@PathVariable Integer id) { repository.deleteById(id); return "redirect:/mesas"; }
}
