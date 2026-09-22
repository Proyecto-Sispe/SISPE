package com.sispe.springboot_web.Service;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

/**
 * Generador mínimo de archivos .xlsx (Excel) sin dependencias externas.
 * Un .xlsx es un ZIP con varios XML; aquí se escriben solo las partes necesarias:
 * hojas con encabezado en negrita, fila fija, filtros automáticos, números como números y anchos de columna.
 */
public final class XlsxWriter {

    private static final DateTimeFormatter FECHA_HORA = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm");
    private static final int ESTILO_NORMAL = 0;
    private static final int ESTILO_ENCABEZADO = 1;
    private static final int ESTILO_DINERO = 2;

    private XlsxWriter() { }

    /** Hoja de cálculo: la primera fila es el encabezado. */
    public record Hoja(String nombre, List<List<Object>> filas, int[] anchos, boolean filtro) { }

    public static byte[] escribir(List<Hoja> hojas) {
        try (ByteArrayOutputStream salida = new ByteArrayOutputStream();
             ZipOutputStream zip = new ZipOutputStream(salida, StandardCharsets.UTF_8)) {
            parte(zip, "[Content_Types].xml", contentTypes(hojas.size()));
            parte(zip, "_rels/.rels", """
                    <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
                    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
                    </Relationships>""");
            parte(zip, "xl/workbook.xml", libro(hojas));
            parte(zip, "xl/_rels/workbook.xml.rels", relacionesLibro(hojas.size()));
            parte(zip, "xl/styles.xml", estilos());
            for (int i = 0; i < hojas.size(); i++) {
                parte(zip, "xl/worksheets/sheet" + (i + 1) + ".xml", hoja(hojas.get(i)));
            }
            zip.finish();
            return salida.toByteArray();
        } catch (IOException e) {
            throw new IllegalStateException("No fue posible generar el archivo Excel", e);
        }
    }

    private static void parte(ZipOutputStream zip, String nombre, String contenido) throws IOException {
        zip.putNextEntry(new ZipEntry(nombre));
        zip.write(contenido.getBytes(StandardCharsets.UTF_8));
        zip.closeEntry();
    }

    private static String contentTypes(int hojas) {
        StringBuilder sb = new StringBuilder("""
                <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
                <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
                <Default Extension="xml" ContentType="application/xml"/>
                <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
                <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
                """);
        for (int i = 1; i <= hojas; i++) {
            sb.append("<Override PartName=\"/xl/worksheets/sheet").append(i)
              .append(".xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml\"/>\n");
        }
        return sb.append("</Types>").toString();
    }

    private static String libro(List<Hoja> hojas) {
        StringBuilder sb = new StringBuilder("""
                <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                <workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
                <sheets>
                """);
        for (int i = 0; i < hojas.size(); i++) {
            sb.append("<sheet name=\"").append(escapar(nombreHoja(hojas.get(i).nombre()))).append("\" sheetId=\"")
              .append(i + 1).append("\" r:id=\"rId").append(i + 1).append("\"/>\n");
        }
        return sb.append("</sheets>\n</workbook>").toString();
    }

    private static String relacionesLibro(int hojas) {
        StringBuilder sb = new StringBuilder("""
                <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
                """);
        for (int i = 1; i <= hojas; i++) {
            sb.append("<Relationship Id=\"rId").append(i)
              .append("\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\" Target=\"worksheets/sheet")
              .append(i).append(".xml\"/>\n");
        }
        sb.append("<Relationship Id=\"rId").append(hojas + 1)
          .append("\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles\" Target=\"styles.xml\"/>\n");
        return sb.append("</Relationships>").toString();
    }

    private static String estilos() {
        return """
                <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                <styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
                <numFmts count="1"><numFmt numFmtId="164" formatCode="#,##0.00"/></numFmts>
                <fonts count="2">
                <font><sz val="11"/><name val="Calibri"/></font>
                <font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>
                </fonts>
                <fills count="3">
                <fill><patternFill patternType="none"/></fill>
                <fill><patternFill patternType="gray125"/></fill>
                <fill><patternFill patternType="solid"><fgColor rgb="FF1F242D"/><bgColor indexed="64"/></patternFill></fill>
                </fills>
                <borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
                <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
                <cellXfs count="3">
                <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
                <xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/>
                <xf numFmtId="164" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>
                </cellXfs>
                <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
                </styleSheet>""";
    }

    private static String hoja(Hoja hoja) {
        List<List<Object>> filas = hoja.filas();
        int columnas = filas.stream().mapToInt(List::size).max().orElse(1);
        StringBuilder sb = new StringBuilder("""
                <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                <worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
                """);
        if (hoja.filtro()) {
            sb.append("<sheetViews><sheetView workbookViewId=\"0\"><pane ySplit=\"1\" topLeftCell=\"A2\" activePane=\"bottomLeft\" state=\"frozen\"/></sheetView></sheetViews>\n");
        }
        if (hoja.anchos() != null && hoja.anchos().length > 0) {
            sb.append("<cols>");
            for (int i = 0; i < hoja.anchos().length; i++) {
                sb.append("<col min=\"").append(i + 1).append("\" max=\"").append(i + 1)
                  .append("\" width=\"").append(hoja.anchos()[i]).append("\" customWidth=\"1\"/>");
            }
            sb.append("</cols>\n");
        }
        sb.append("<sheetData>\n");
        for (int r = 0; r < filas.size(); r++) {
            sb.append("<row r=\"").append(r + 1).append("\">");
            List<Object> fila = filas.get(r);
            for (int c = 0; c < fila.size(); c++) {
                celda(sb, referencia(c, r + 1), fila.get(c), r == 0 && hoja.filtro());
            }
            sb.append("</row>\n");
        }
        sb.append("</sheetData>\n");
        if (hoja.filtro() && filas.size() > 1) {
            sb.append("<autoFilter ref=\"A1:").append(referencia(columnas - 1, filas.size())).append("\"/>\n");
        }
        return sb.append("</worksheet>").toString();
    }

    private static void celda(StringBuilder sb, String ref, Object valor, boolean encabezado) {
        if (valor == null) return;
        if (valor instanceof BigDecimal dinero) {
            sb.append("<c r=\"").append(ref).append("\" s=\"").append(ESTILO_DINERO).append("\"><v>")
              .append(dinero.toPlainString()).append("</v></c>");
        } else if (valor instanceof Integer || valor instanceof Long || valor instanceof Short) {
            sb.append("<c r=\"").append(ref).append("\"><v>").append(valor).append("</v></c>");
        } else if (valor instanceof Double || valor instanceof Float) {
            sb.append("<c r=\"").append(ref).append("\" s=\"").append(ESTILO_DINERO).append("\"><v>").append(valor).append("</v></c>");
        } else {
            String texto = valor instanceof LocalDateTime fh ? fh.format(FECHA_HORA)
                    : valor instanceof LocalDate d ? d.toString() : valor.toString();
            sb.append("<c r=\"").append(ref).append("\" t=\"inlineStr\" s=\"")
              .append(encabezado ? ESTILO_ENCABEZADO : ESTILO_NORMAL).append("\"><is><t xml:space=\"preserve\">")
              .append(escapar(texto)).append("</t></is></c>");
        }
    }

    /** Referencia tipo A1, B2… (columna base 0, fila base 1). */
    static String referencia(int columna, int fila) {
        StringBuilder letras = new StringBuilder();
        int n = columna;
        do {
            letras.insert(0, (char) ('A' + n % 26));
            n = n / 26 - 1;
        } while (n >= 0);
        return letras.toString() + fila;
    }

    /** Excel limita los nombres de hoja a 31 caracteres y prohíbe algunos símbolos. */
    private static String nombreHoja(String nombre) {
        String limpio = nombre.replaceAll("[\\\\/?*\\[\\]:]", " ").trim();
        if (limpio.isEmpty()) limpio = "Hoja";
        return limpio.length() > 31 ? limpio.substring(0, 31) : limpio;
    }

    private static String escapar(String texto) {
        StringBuilder sb = new StringBuilder(texto.length() + 16);
        for (int i = 0; i < texto.length(); i++) {
            char ch = texto.charAt(i);
            switch (ch) {
                case '&' -> sb.append("&amp;");
                case '<' -> sb.append("&lt;");
                case '>' -> sb.append("&gt;");
                case '"' -> sb.append("&quot;");
                default -> {
                    boolean valido = ch == '\t' || ch == '\n' || ch == '\r' || ch >= 0x20;
                    if (valido) sb.append(ch); // se descartan caracteres de control que vuelven inválido el XML
                }
            }
        }
        return sb.toString();
    }
}
