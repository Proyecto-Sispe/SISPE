package com.sispe.springboot_web.Controller;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.math.BigDecimal;
import java.time.LocalDate;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.ResponseEntity;
import org.springframework.ui.Model;
import org.springframework.validation.BeanPropertyBindingResult;
import org.springframework.validation.BindingResult;

import com.sispe.springboot_web.Service.ConsultaMultitabla.Resumen;
import com.sispe.springboot_web.Service.ReporteMultitablaService;
import com.sispe.springboot_web.Service.ReporteService;
import com.sispe.springboot_web.dto.FiltrosReporte;

@ExtendWith(MockitoExtension.class)
class ReporteControllerTest {

    @Mock
    private ReporteService service;
    @Mock
    private ReporteMultitablaService multitabla;
    @Mock
    private Model model;

    private ReporteController controller;
    private final BindingResult sinErrores = new BeanPropertyBindingResult(new FiltrosReporte(), "f");

    @BeforeEach
    void setUp() {
        controller = new ReporteController(service, multitabla);
    }

    @Test
    void indexRechazaUnRangoDeFechasInvertido() {
        when(service.datos(any(), any(), any(), any(), any())).thenReturn(java.util.Map.of());

        String vista = controller.index(LocalDate.of(2026, 9, 20), LocalDate.of(2026, 9, 1), "", null, "", model);

        assertEquals("reportes/index", vista);
        verify(model).addAttribute("error",
                "La fecha «Hasta» no puede ser anterior a «Desde». Corrige el rango para ver resultados.");
    }

    @Test
    void indexPasaLasFechasCompletasAlServicio() {
        when(service.datos(any(), any(), any(), any(), any())).thenReturn(java.util.Map.of());

        controller.index(LocalDate.of(2026, 9, 1), LocalDate.of(2026, 9, 30), "entregado", 3L, "urgente", model);

        verify(service).datos(
                LocalDate.of(2026, 9, 1).atStartOfDay(),
                LocalDate.of(2026, 9, 30).atTime(23, 59, 59, 999_999_999),
                "entregado", 3L, "urgente");
    }

    @Test
    void multitablaCargaLasListasDesplegablesYElResultado() {
        when(multitabla.categorias()).thenReturn(java.util.List.of());
        when(multitabla.productos()).thenReturn(java.util.List.of());
        when(multitabla.metodosPago()).thenReturn(java.util.List.of());
        Resumen resumen = new Resumen(1, 1, 1, BigDecimal.TEN, BigDecimal.TEN);
        ReporteMultitablaService.Resultado resultado = new ReporteMultitablaService.Resultado(
                java.util.List.of(), false, resumen);
        when(multitabla.consultar(any(), eq(ReporteMultitablaService.MAX_PANTALLA))).thenReturn(resultado);

        String vista = controller.multitabla(new FiltrosReporte(), sinErrores, model);

        assertEquals("reportes/multitabla", vista);
        verify(model).addAttribute("resumen", resumen);
        verify(model, never()).addAttribute(eq("error"), any());
    }

    @Test
    void multitablaNoConsultaSiElRangoDeFechasEsInvalido() {
        when(multitabla.categorias()).thenReturn(java.util.List.of());
        when(multitabla.productos()).thenReturn(java.util.List.of());
        when(multitabla.metodosPago()).thenReturn(java.util.List.of());
        FiltrosReporte filtros = new FiltrosReporte();
        filtros.setDesde(LocalDate.of(2026, 9, 20));
        filtros.setHasta(LocalDate.of(2026, 9, 1));

        String vista = controller.multitabla(filtros, sinErrores, model);

        assertEquals("reportes/multitabla", vista);
        verify(multitabla, never()).consultar(any(), anyInt());
        verify(model).addAttribute("error",
                "La fecha «Hasta» no puede ser anterior a «Desde». Corrige el rango para ver resultados.");
    }

    @Test
    void multitablaExcelRechazaFiltrosInvalidosSinConsultarLaBaseDeDatos() {
        FiltrosReporte filtros = new FiltrosReporte();
        filtros.setDesde(LocalDate.of(2026, 9, 20));
        filtros.setHasta(LocalDate.of(2026, 9, 1));

        ResponseEntity<byte[]> respuesta = controller.multitablaExcel(filtros, sinErrores);

        assertEquals(400, respuesta.getStatusCode().value());
        verify(multitabla, never()).consultar(any(), anyInt());
    }

    @Test
    void multitablaPdfUsaElLimiteDeExportacionYDevuelveElArchivoAdjunto() {
        Resumen resumen = new Resumen(0, 0, 0, BigDecimal.ZERO, BigDecimal.ZERO);
        ReporteMultitablaService.Resultado resultado = new ReporteMultitablaService.Resultado(
                java.util.List.of(), false, resumen);
        FiltrosReporte filtros = new FiltrosReporte();
        when(multitabla.consultar(filtros, ReporteMultitablaService.MAX_EXPORTACION)).thenReturn(resultado);
        when(multitabla.pdf(resultado, filtros)).thenReturn(new byte[]{1, 2, 3});

        ResponseEntity<byte[]> respuesta = controller.multitablaPdf(filtros, sinErrores);

        assertEquals(200, respuesta.getStatusCode().value());
        assertEquals("attachment; filename=reporte-multitabla.pdf",
                respuesta.getHeaders().getFirst("Content-Disposition"));
    }
}
