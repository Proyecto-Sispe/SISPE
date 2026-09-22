package com.sispe.springboot_web.Controller;

import com.sispe.springboot_web.Service.ReporteMultitablaService;
import com.sispe.springboot_web.Service.ReporteService;
import com.sispe.springboot_web.dto.FiltrosReporte;
import org.springframework.dao.DataAccessException;
import org.springframework.validation.BindingResult;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.*;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.Map;


@Controller @RequestMapping("/reportes")
@PreAuthorize("hasRole('ADMINISTRADOR')")
public class ReporteController {
    private final ReporteService service;
    private final ReporteMultitablaService multitabla;
    public ReporteController(ReporteService service, ReporteMultitablaService multitabla) {
        this.service = service;
        this.multitabla = multitabla;
    }

    /**
     * Filtros multicriterio: rango de fechas (ambas inclusivas, día completo), estado, mesa y prioridad.
     * Todos son opcionales y se combinan con AND.
     */
    @GetMapping public String index(
            @RequestParam(required=false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate desde,
            @RequestParam(required=false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate hasta,
            @RequestParam(required=false, defaultValue="") String estado,
            @RequestParam(required=false) Long mesa,
            @RequestParam(required=false, defaultValue="") String prioridad, Model model) {
        if (desde != null && hasta != null && hasta.isBefore(desde)) {
            model.addAttribute("error", "La fecha «Hasta» no puede ser anterior a «Desde». Corrige el rango para ver resultados.");
        }
        Map<String,Object> datos = consultar(desde, hasta, estado, mesa, prioridad);
        model.addAllAttributes(datos);
        model.addAttribute("desde", desde); model.addAttribute("hasta", hasta);
        model.addAttribute("estado", estado); model.addAttribute("mesa", mesa); model.addAttribute("prioridad", prioridad);
        return "reportes/index";
    }

    @GetMapping("/pdf/{tipo}") public ResponseEntity<byte[]> pdf(@PathVariable String tipo,
            @RequestParam(required=false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate desde,
            @RequestParam(required=false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate hasta,
            @RequestParam(required=false) String estado,
            @RequestParam(required=false) Long mesa,
            @RequestParam(required=false) String prioridad) {
        byte[] pdf = service.pdf(tipo, consultar(desde, hasta, estado, mesa, prioridad));
        return ResponseEntity.ok().header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=reporte-" + tipo + ".pdf").contentType(MediaType.APPLICATION_PDF).body(pdf);
    }

    private Map<String,Object> consultar(LocalDate desde, LocalDate hasta, String estado, Long mesa, String prioridad) {
        LocalDateTime inicio = desde == null ? null : desde.atStartOfDay();
        LocalDateTime fin = hasta == null ? null : hasta.atTime(LocalTime.MAX);
        return service.datos(inicio, fin, estado, mesa, prioridad);
    }

    // ------------------------------------------------------------------------------------
    // Reporte multitabla: joins entre pedidos, mesas, clientes, meseros, productos, categorías,
    // adiciones, facturas y métodos de pago. Se ve en pantalla y se descarga en PDF o Excel.
    // ------------------------------------------------------------------------------------

    @GetMapping("/multitabla")
    public String multitabla(@ModelAttribute("f") FiltrosReporte filtros, BindingResult binding, Model model) {
        String problema = binding.hasErrors()
                ? "Alguno de los filtros tiene un formato no válido (revisa las fechas y los números)."
                : filtros.problema();
        try {
            model.addAttribute("categorias", multitabla.categorias());
            model.addAttribute("productos", multitabla.productos());
            model.addAttribute("metodos", multitabla.metodosPago());
            if (problema == null) {
                var resultado = multitabla.consultar(filtros, ReporteMultitablaService.MAX_PANTALLA);
                model.addAttribute("filas", resultado.filas());
                model.addAttribute("resumen", resultado.resumen());
                model.addAttribute("truncado", resultado.truncado());
            }
        } catch (DataAccessException ex) {
            problema = "No se pudo consultar la base de datos. Verifica que MySQL esté en ejecución.";
        }
        if (problema != null) {
            model.addAttribute("error", problema);
            model.addAttribute("filas", java.util.List.of());
        }
        model.addAttribute("maxPantalla", ReporteMultitablaService.MAX_PANTALLA);
        return "reportes/multitabla";
    }

    @GetMapping("/multitabla/pdf")
    public ResponseEntity<byte[]> multitablaPdf(@ModelAttribute("f") FiltrosReporte filtros, BindingResult binding) {
        var resultado = exportable(filtros, binding);
        if (resultado == null) return ResponseEntity.badRequest().build();
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=reporte-multitabla.pdf")
                .contentType(MediaType.APPLICATION_PDF)
                .body(multitabla.pdf(resultado, filtros));
    }

    @GetMapping("/multitabla/excel")
    public ResponseEntity<byte[]> multitablaExcel(@ModelAttribute("f") FiltrosReporte filtros, BindingResult binding) {
        var resultado = exportable(filtros, binding);
        if (resultado == null) return ResponseEntity.badRequest().build();
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=reporte-multitabla.xlsx")
                .contentType(MediaType.parseMediaType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
                .body(multitabla.excel(resultado, filtros));
    }

    /** Consulta para exportar; devuelve null si los filtros no son válidos. */
    private ReporteMultitablaService.Resultado exportable(FiltrosReporte filtros, BindingResult binding) {
        if (binding.hasErrors() || filtros.problema() != null) return null;
        return multitabla.consultar(filtros, ReporteMultitablaService.MAX_EXPORTACION);
    }
}
