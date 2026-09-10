package com.sispe.springboot_web.Controller;

import com.sispe.springboot_web.Service.ReporteService;
import org.springframework.http.*;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDate;
import java.util.Map;

@Controller @RequestMapping("/reportes")
public class ReporteController {
    private final ReporteService service;
    public ReporteController(ReporteService service) { this.service = service; }
    @GetMapping public String index(@RequestParam(required=false) LocalDate desde, @RequestParam(required=false) LocalDate hasta,
            @RequestParam(required=false, defaultValue="") String tipo, @RequestParam(required=false, defaultValue="") String estado, Model model) {
        Map<String,Object> datos = service.datos(desde, hasta, tipo, estado); model.addAllAttributes(datos); model.addAttribute("desde", desde); model.addAttribute("hasta", hasta); model.addAttribute("tipo", tipo); model.addAttribute("estado", estado); return "reportes/index";
    }
    @GetMapping("/pdf/{tipo}") public ResponseEntity<byte[]> pdf(@PathVariable String tipo, @RequestParam(required=false) LocalDate desde, @RequestParam(required=false) LocalDate hasta, @RequestParam(required=false) String estado) {
        byte[] pdf = service.pdf("Reporte " + tipo, service.datos(desde, hasta, tipo, estado));
        return ResponseEntity.ok().header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=reporte-" + tipo + ".pdf").contentType(MediaType.APPLICATION_PDF).body(pdf);
    }
}
