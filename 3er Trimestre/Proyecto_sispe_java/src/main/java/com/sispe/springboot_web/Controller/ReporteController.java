package com.sispe.springboot_web.Controller;

import com.sispe.springboot_web.Service.ReporteService;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.*;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;
import java.time.LocalDate;
import java.util.Map;


@Controller @RequestMapping("/reportes")
@PreAuthorize("hasRole('ADMINISTRADOR')")
public class ReporteController {
    private final ReporteService service;
    public ReporteController(ReporteService service) { this.service = service; }

    @GetMapping public String index(
            @RequestParam(required=false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate desde,
            @RequestParam(required=false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate hasta,
            @RequestParam(required=false, defaultValue="") String estado, Model model) {
        Map<String,Object> datos = service.datos(desde, hasta, estado);
        model.addAllAttributes(datos);
        model.addAttribute("desde", desde); model.addAttribute("hasta", hasta); model.addAttribute("estado", estado);
        return "reportes/index";
    }

    @GetMapping("/pdf/{tipo}") public ResponseEntity<byte[]> pdf(@PathVariable String tipo,
            @RequestParam(required=false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate desde,
            @RequestParam(required=false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate hasta,
            @RequestParam(required=false) String estado) {
        byte[] pdf = service.pdf(tipo, service.datos(desde, hasta, estado));
        return ResponseEntity.ok().header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=reporte-" + tipo + ".pdf").contentType(MediaType.APPLICATION_PDF).body(pdf);
    }
}
