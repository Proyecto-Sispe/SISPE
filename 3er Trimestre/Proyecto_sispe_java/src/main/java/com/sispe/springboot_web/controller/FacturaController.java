// Controller/FacturaController.java
package com.sispe.springboot_web.controller;

import com.sispe.springboot_web.repository.FacturaRepository;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
@RequestMapping("/facturas")
public class FacturaController {
    private final FacturaRepository facturas;
    public FacturaController(FacturaRepository facturas) { this.facturas = facturas; }
    @GetMapping public String index(Model model) { model.addAttribute("facturas", facturas.findAll()); return "facturas/index"; }
}