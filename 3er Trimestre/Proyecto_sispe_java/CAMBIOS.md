# Cambios aplicados a SISPE (según observaciones del evaluador)

> Importante: estos cambios NO se compilaron ni se probaron (no había acceso a Maven Central).
> Antes de entregar ejecuta `.\mvnw.cmd clean verify` y prueba a mano cada flujo.

## Observación 1 — CRUD, errores en pedidos, inventario, notificaciones
- Repository/DetallePedidoRepository y DetallePedidoAdicionRepository: `@Transactional` en los `deleteBy…`
  (causa probable del error al eliminar productos del pedido).
- Repository/MenuInsumoRepository: `deleteByInsumo_Id`.
- Service/PedidoService: el descuento de inventario ocurre al pasar a "entregado" (cocina, mesero o API), una sola vez.
- Controller/PedidoController: edición real (antes "Actualizar" creaba duplicados), validación de mesa/estado/prioridad/tiempo,
  prioridad alineada con el ENUM de la BD (normal/urgente; "alta" hacía fallar el insert), campos del formulario restringidos, mensajes.
- Controller/ClienteController: no se puede quitar/vaciar productos de un pedido confirmado; mensajes de éxito/error.
- Controller/CocinaController y PedidoApiController: excepciones controladas (sin página de error genérica).
- Controller/MesaController: validaciones, mesa duplicada, error amigable al eliminar con pedidos asociados.
- Controller/MenuController: mensajes al guardar/eliminar (firma `eliminar(Integer)` conservada por los tests).
- Inventario (InventarioService/InventarioController/admin/inventario.html): editar stock, eliminar insumo,
  quitar ingrediente de receta, validaciones, alerta de stock bajo, tabla de recetas.

- Panel de cocina (CocinaController + cocina/index.html): cada pedido muestra sus productos, cantidades, adiciones y notas del cliente.

## Observación 2 — Reportes
- ReporteController/ReporteService/reportes/index.html: fechas (día completo, inclusivas), filtros de estado, mesa y prioridad,
  el estado se conserva al filtrar, tablas de ventas por producto y facturas; los PDF usan el mismo filtro.
  (Se conserva `datos(desde, hasta, estado)` para no romper ReporteServiceTest.)

## Observación 3 — Usabilidad y retroalimentación
- templates/fragments/alertas.html: avisos ok/error reutilizables.
- static/js/sispe.js: confirmaciones (`data-confirm`), bloqueo de doble envío, avisos de éxito que se ocultan solos.
- static/css/sispe.css: estilos de avisos, stock bajo y edición en línea.
- Fragmento aplicado en pedidos, mesas, cocina, menú (admin y cliente), pedido y pago del cliente, inventario y reportes.


## Reporte multitabla (nuevo) — /reportes/multitabla

Cruza en una sola consulta SQL (joins reales, no varias consultas por separado): Pedido, Mesa,
Sesion_Mesa (cliente), Persona (mesero), Detalle_Pedido, Menu, Categoria, Detalle_Pedido_Adicion +
Adicion, Factura y Factura_has_Metodo_pago + Metodo_pago.

- Filtros combinables (AND): fecha desde/hasta (inclusive), estado, prioridad, mesa, categoría,
  producto y método de pago. Los combos de categoría/producto/método salen de la propia base de datos.
- Se ve en pantalla (hasta 500 filas) con totales (pedidos, unidades, total de líneas, total facturado).
- Descarga en PDF (misma consulta, tabla horizontal) y en Excel/.xlsx (dos hojas: datos con filtro
  automático + hoja de filtros y totales), ambos hasta 20.000 filas.
- El .xlsx se genera sin librerías externas (Service/XlsxWriter.java); el PDF reutiliza OpenPDF,
  que el proyecto ya usa en FacturaPdfService.
- Archivos: dto/FiltrosReporte.java, Service/ConsultaMultitabla.java, Service/XlsxWriter.java,
  Service/ReporteMultitablaService.java, Controller/ReporteController.java (3 endpoints nuevos),
  templates/reportes/multitabla.html.
- Corregido de paso: src/main/resources/db/sistema.sql creaba Menu_Insumo antes que Menu (fallaba
  con error 1005 al importar el script); se movió al final, donde ya existen las tablas de las que depende.

### Cómo se probó
No se pudo compilar el proyecto completo (Maven Central no es accesible en este entorno), así que
se probó por partes, con datos reales:
- La consulta SQL (Service/ConsultaMultitabla.java) se ejecutó contra una base MySQL/MariaDB local
  cargada con `sistema.sql` y datos de prueba: 12 combinaciones de filtros (individuales, combinados,
  vacíos y un intento de inyección SQL) devolvieron el número de filas esperado.
- El archivo .xlsx generado por Service/XlsxWriter.java se abrió con la librería openpyxl (Python) y
  se comprobó que las hojas, el encabezado en negrita, el filtro automático, los anchos de columna y
  los números con formato de moneda quedan correctos, incluyendo textos con tildes, símbolos y saltos
  de línea.
- El código del PDF (Service/ReporteMultitablaService.pdf) no se pudo ejecutar (no hay acceso al jar
  de OpenPDF en este entorno), pero usa exactamente la misma API que ya funciona en
  Service/FacturaPdfService.java (PdfPTable, PdfPCell, FontFactory, etc.), así que el riesgo es bajo.
  Pruébalo generando un PDF desde /reportes/multitabla/pdf antes de dar esto por cerrado.


## Pruebas nuevas (56) — para la observación 4 del informe de calidad

Se agregaron 56 métodos `@Test` (JUnit 5 + Mockito), siguiendo el mismo estilo que ya usaba el
proyecto (instanciación directa del controller/service con mocks, sin `MockMvc`). El total pasa
de 57 a 113 pruebas.

| Archivo | Pruebas | Cubre |
|---|---|---|
| Service/PedidoServiceTest.java (nuevo) | 8 | Transiciones de estado, descuento de inventario ligado a "entregado", que no se duplique, que un pedido entregado no retroceda |
| Service/InventarioServiceTest.java (ampliado, +5) | 5 nuevas | actualizar stock, desactivar insumo (y su baja en cascada de recetas), eliminar receta, guardar receta nueva |
| Service/ConsultaMultitablaTest.java (nuevo) | 6 | Construcción del SQL según cada filtro, que los filtros de texto vayan como parámetros (no concatenados), agregación de totales sin duplicar facturas |
| Service/XlsxWriterTest.java (nuevo) | 7 | Estructura del .xlsx generado (ZIP + XML), referencias de celda tipo Excel, números vs texto, escape de caracteres especiales, nombres de hoja largos |
| Controller/PedidoControllerTest.java (nuevo) | 12 | Validación del formulario (mesa, prioridad), que "guardar" solo cree y no reutilice el id, edición real, mensajes de error de base de datos |
| Controller/InventarioControllerTest.java (nuevo) | 12 | Validación de stocks, insumo duplicado, receta con producto inexistente, cantidad inválida |
| Controller/ReporteControllerTest.java (nuevo) | 6 | Rango de fechas inválido (en el reporte básico y en el multitabla), que un filtro inválido no llegue a consultar la base de datos, cabeceras de descarga del PDF |

No se pudieron compilar ni ejecutar (no hay acceso a los `.jar` de JUnit/Mockito en este entorno),
así que revísalas con `mvn clean verify` antes de confiar en ellas. Si alguna falla por un detalle
de firma o de mensaje exacto, es la prueba la que hay que ajustar, no asumas que el código de
producción está mal sin revisar primero.

## Informe de verificación y validación (nuevo) — INFORME_VERIFICACION_VALIDACION.md

Plantilla con las tablas que pide la observación 4 (pruebas, resultados, cobertura JaCoCo,
casos de prueba relevantes, defectos corregidos). Las celdas marcadas `⟨completar⟩` se llenan
con los números reales de `mvn clean verify` — el archivo trae, al final, el paso a paso de
dónde sacar cada uno (surefire-reports y target/site/jacoco).

## Observación 4 — Calidad (pendiente)
- No incluido: informe V&V con métricas reales. Salen de `mvn clean verify` (surefire + jacoco).
- Inconsistencias a corregir: CALIDAD.md dice 45 pruebas (hay 57 @Test) y menciona `jacoco:check` al 80 %
  que el pom.xml no tiene. Faltan pruebas para PedidoService, ClienteController, PedidoController, FacturaService,
  InventarioController y ReporteController.

## Seguridad
- application.properties contiene contraseñas (MySQL y Gmail) en texto plano: pásalas a variables de entorno.
