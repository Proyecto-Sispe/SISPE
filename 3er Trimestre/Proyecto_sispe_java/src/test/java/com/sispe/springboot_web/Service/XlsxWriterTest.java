package com.sispe.springboot_web.Service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

import org.junit.jupiter.api.Test;

/**
 * XlsxWriter arma el .xlsx a mano (sin Apache POI), así que estas pruebas validan directamente la
 * estructura del ZIP y el XML que produce: que Excel pueda abrirlo depende de que esas partes
 * existan y sean XML válido. El archivo generado también se abrió manualmente con una librería de
 * Python (openpyxl) para confirmar que Excel lo interpreta como se espera (ver CAMBIOS.md).
 */
class XlsxWriterTest {

    private Map<String, String> leerPartes(byte[] xlsx) throws Exception {
        Map<String, String> partes = new HashMap<>();
        try (ZipInputStream zip = new ZipInputStream(new ByteArrayInputStream(xlsx))) {
            ZipEntry entrada;
            while ((entrada = zip.getNextEntry()) != null) {
                partes.put(entrada.getName(), new String(zip.readAllBytes(), StandardCharsets.UTF_8));
            }
        }
        return partes;
    }

    @Test
    void generaUnZipConLasPartesMinimasDeUnXlsx() throws Exception {
        XlsxWriter.Hoja hoja = new XlsxWriter.Hoja("Datos", List.of(List.of("A", "B")), new int[]{10, 10}, false);

        Map<String, String> partes = leerPartes(XlsxWriter.escribir(List.of(hoja)));

        Set<String> esperadas = Set.of("[Content_Types].xml", "_rels/.rels", "xl/workbook.xml",
                "xl/_rels/workbook.xml.rels", "xl/styles.xml", "xl/worksheets/sheet1.xml");
        assertEquals(esperadas, partes.keySet());
        assertTrue(partes.get("xl/workbook.xml").contains("name=\"Datos\""));
    }

    @Test
    void cadaHojaProduceSuPropioArchivoYSuPropiaEntradaEnElLibro() throws Exception {
        XlsxWriter.Hoja uno = new XlsxWriter.Hoja("Reporte", List.of(List.of("x")), null, true);
        XlsxWriter.Hoja dos = new XlsxWriter.Hoja("Filtros", List.of(List.of("y")), null, false);

        Map<String, String> partes = leerPartes(XlsxWriter.escribir(List.of(uno, dos)));

        assertTrue(partes.containsKey("xl/worksheets/sheet1.xml"));
        assertTrue(partes.containsKey("xl/worksheets/sheet2.xml"));
        assertTrue(partes.get("xl/workbook.xml").contains("r:id=\"rId1\""));
        assertTrue(partes.get("xl/workbook.xml").contains("r:id=\"rId2\""));
    }

    @Test
    void soloLaHojaConFiltroActivadoIncluyeAutoFilter() throws Exception {
        XlsxWriter.Hoja conFiltro = new XlsxWriter.Hoja("Reporte", List.of(List.of("Col"), List.of("x")), null, true);
        XlsxWriter.Hoja sinFiltro = new XlsxWriter.Hoja("Totales", List.of(List.of("Col"), List.of("x")), null, false);

        Map<String, String> partes = leerPartes(XlsxWriter.escribir(List.of(conFiltro, sinFiltro)));

        assertTrue(partes.get("xl/worksheets/sheet1.xml").contains("<autoFilter"));
        assertTrue(!partes.get("xl/worksheets/sheet2.xml").contains("<autoFilter"));
    }

    @Test
    void losNumerosDecimalesQuedanComoValoresNumericosNoComoTexto() throws Exception {
        XlsxWriter.Hoja hoja = new XlsxWriter.Hoja("Reporte",
                List.of(List.of("Total"), List.of(new BigDecimal("36000.00"))), null, false);

        String xml = leerPartes(XlsxWriter.escribir(List.of(hoja))).get("xl/worksheets/sheet1.xml");

        // La celda con el BigDecimal debe llevar estilo de dinero (s="2") y un <v> numérico plano,
        // sin marcarse como texto (t="inlineStr", que sí lleva la cabecera "Total").
        assertTrue(xml.contains("<c r=\"A2\" s=\"2\"><v>36000.00</v></c>"));
        assertTrue(xml.contains("t=\"inlineStr\""), "la cabecera de texto sí debe ir como inlineStr");
    }

    @Test
    void escapaCaracteresEspecialesYDescartaCaracteresDeControlInvalidosEnXml() throws Exception {
        String textoConProblemas = "Ñoño & <café> \"pedido\" \u0001";
        XlsxWriter.Hoja hoja = new XlsxWriter.Hoja("Reporte", List.of(List.of(textoConProblemas)), null, false);

        String xml = leerPartes(XlsxWriter.escribir(List.of(hoja))).get("xl/worksheets/sheet1.xml");

        assertTrue(xml.contains("&amp;"));
        assertTrue(xml.contains("&lt;café&gt;"));
        assertTrue(xml.contains("&quot;pedido&quot;"));
        assertTrue(!xml.contains("\u0001"), "los caracteres de control no son válidos en XML y deben descartarse");
    }

    @Test
    void unNombreDeHojaLargoOConSimbolosProhibidosSeRecorta() throws Exception {
        String nombreLargo = "Reporte de pedidos filtrados por fecha, mesa y categoría";
        XlsxWriter.Hoja hoja = new XlsxWriter.Hoja(nombreLargo, List.of(List.of("x")), null, false);

        String libro = leerPartes(XlsxWriter.escribir(List.of(hoja))).get("xl/workbook.xml");

        // Excel limita los nombres de hoja a 31 caracteres.
        int inicio = libro.indexOf("name=\"") + 6;
        int fin = libro.indexOf('"', inicio);
        assertTrue(fin - inicio <= 31);
    }

    @Test
    void unaHojaVaciaNoRompeLaGeneracion() throws Exception {
        XlsxWriter.Hoja vacia = new XlsxWriter.Hoja("Sin datos", List.of(), null, true);

        byte[] xlsx = XlsxWriter.escribir(List.of(vacia));

        assertTrue(xlsx.length > 0);
    }
}
