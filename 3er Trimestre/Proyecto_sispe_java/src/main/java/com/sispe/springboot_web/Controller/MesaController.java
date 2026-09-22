
package com.sispe.springboot_web.Controller;

import org.springframework.dao.DataAccessException;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import com.sispe.springboot_web.Model.Mesa;
import com.sispe.springboot_web.Repository.MesaRepository;
import com.sispe.springboot_web.Service.QrService;

import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;

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

    @GetMapping("/mesas/guardar")
    public String formularioGuardar() {
        return "redirect:/mesas";
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
    public String guardar(@ModelAttribute Mesa mesa, RedirectAttributes attrs) {
        String problema = validar(mesa);
        if (problema != null) {
            attrs.addFlashAttribute("error", problema);
        } else if (mesa.getId() != null && repository.existsById(mesa.getId())) {
            attrs.addFlashAttribute("error", "Ya existe la mesa " + mesa.getId() + ". Usa «Actualizar» para modificarla.");
        } else {
            repository.save(mesa);
            attrs.addFlashAttribute("ok", "Mesa " + mesa.getId() + " creada correctamente.");
        }
        return "redirect:/mesas";
    }

    @PostMapping("/mesas/actualizar/{id}")
    public String actualizar(@PathVariable Integer id, @ModelAttribute Mesa mesa, RedirectAttributes attrs) {
        mesa.setId(id);
        String problema = validar(mesa);
        if (problema != null) {
            attrs.addFlashAttribute("error", problema);
        } else {
            repository.save(mesa);
            attrs.addFlashAttribute("ok", "Mesa " + id + " actualizada.");
        }
        return "redirect:/mesas";
    }

    @PostMapping("/mesas/eliminar/{id}")
    public String eliminar(@PathVariable Integer id, RedirectAttributes attrs) {
        try {
            repository.deleteById(id);
            attrs.addFlashAttribute("ok", "Mesa " + id + " eliminada.");
        } catch (DataAccessException ex) {
            attrs.addFlashAttribute("error", "No se puede eliminar la mesa " + id + " porque tiene pedidos o sesiones asociados.");
        }
        return "redirect:/mesas";
    }

    private String validar(Mesa mesa) {
        if (mesa.getId() == null || mesa.getId() < 1) return "El número de mesa debe ser mayor que cero.";
        if (mesa.getCapacidad() == null || mesa.getCapacidad() < 1) return "La capacidad debe ser de al menos 1 persona.";
        if (mesa.getUbicacion() == null || mesa.getUbicacion().isBlank()) return "La ubicación es obligatoria.";
        if (mesa.getUbicacion().length() > 50) return "La ubicación admite máximo 50 caracteres.";
        if (mesa.getOcupada() == null) mesa.setOcupada(false);
        return null;
    }
}