package com.login.demo.controller;

import com.login.demo.model.Mesa;
import com.login.demo.repository.MesaRepository;
import com.login.demo.service.QrService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;

@Controller
@RequiredArgsConstructor
public class MesaController {
    private final MesaRepository repository;
    private final QrService qrService;

    @GetMapping("/mesas")
    public String index(Model model) {
        model.addAttribute("mesas", repository.findAll());
        return "mesas/index";
    }

    @PostMapping("/mesas/{id}/habilitar")
    public String habilitar(@PathVariable Integer id, HttpServletRequest request) {
        Mesa mesa = repository.findById(id).orElseThrow();
        mesa.setOcupada(false);
        repository.save(mesa);
        return "redirect:/mesas";
    }

    @GetMapping(value = "/mesas/{id}/qr", produces = MediaType.IMAGE_PNG_VALUE)
    @ResponseBody
    public ResponseEntity<byte[]> qr(@PathVariable Integer id, HttpServletRequest request) {
        if (!repository.existsById(id)) throw new ResponseStatusException(org.springframework.http.HttpStatus.NOT_FOUND, "Mesa no encontrada");
        String base = request.getRequestURL().toString().replace(request.getRequestURI(), "");
        return ResponseEntity.ok().contentType(MediaType.IMAGE_PNG).body(qrService.generarPng(base + "/cliente/escanear/" + id));
    }

    @GetMapping(value = "/mesas/{id}/qr/descargar", produces = MediaType.IMAGE_PNG_VALUE)
    @ResponseBody
    public ResponseEntity<byte[]> descargarQr(@PathVariable Integer id, HttpServletRequest request) {
        ResponseEntity<byte[]> qr = qr(id, request);
        return ResponseEntity.ok().contentType(MediaType.IMAGE_PNG).header("Content-Disposition", "attachment; filename=mesa-" + id + ".png").body(qr.getBody());
    }
    @PostMapping("/mesas/guardar")
    public String guardar(@ModelAttribute Mesa mesa) { repository.save(mesa); return "redirect:/mesas"; }
    @PostMapping("/mesas/eliminar/{id}")
    public String eliminar(@PathVariable Integer id) { repository.deleteById(id); return "redirect:/mesas"; }
}
