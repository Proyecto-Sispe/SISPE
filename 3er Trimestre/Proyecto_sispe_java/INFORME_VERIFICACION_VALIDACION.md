# Informe de verificación y validación — SISPE

> Plantilla lista para llenar. Las tablas marcadas `⟨completar⟩` se llenan con los resultados
> reales de tu máquina, no con estimaciones. Ver la sección "Cómo obtener cada número" al final.

## 1. Alcance

Este informe cubre las pruebas automatizadas del backend (JUnit 5 + Mockito) que corren con
`mvn clean verify`. No cubre pruebas manuales de interfaz ni pruebas de carga.

## 2. Estrategia de pruebas

| Nivel | Qué se prueba | Herramienta |
|---|---|---|
| Unitaria (Service) | Reglas de negocio: transiciones de pedido, descuento de inventario, construcción de SQL, generación de Excel | JUnit 5 + Mockito |
| Unitaria (Controller) | Validación de formularios, manejo de errores, mensajes al usuario | JUnit 5 + Mockito (instanciación directa, sin `MockMvc`) |
| Integración manual | Consulta multitabla contra MySQL/MariaDB real con datos de prueba | Ejecución manual (ver `CAMBIOS.md`) |

## 3. Resultado de la ejecución — `mvn clean verify`

Ejecuta:

```
mvnw.cmd clean verify
```

y copia aquí lo que reporte Surefire al final (busca la línea `Tests run: ...`):

| Métrica | Valor |
|---|---|
| Pruebas ejecutadas | ⟨completar⟩ |
| Fallidas | ⟨completar⟩ |
| Con error | ⟨completar⟩ |
| Omitidas | ⟨completar⟩ |
| Tiempo total | ⟨completar⟩ |
| Build | ⟨SUCCESS / FAILURE⟩ |

### Desglose por clase

Abre `target/surefire-reports/` y llena una fila por cada `TEST-*.xml` (o usa el resumen que
imprime la consola):

| Clase de prueba | Pruebas | Fallidas | Errores | Tiempo (s) |
|---|---|---|---|---|
| PedidoServiceTest | ⟨completar⟩ | | | |
| InventarioServiceTest | ⟨completar⟩ | | | |
| ConsultaMultitablaTest | ⟨completar⟩ | | | |
| XlsxWriterTest | ⟨completar⟩ | | | |
| PedidoControllerTest | ⟨completar⟩ | | | |
| InventarioControllerTest | ⟨completar⟩ | | | |
| ReporteControllerTest | ⟨completar⟩ | | | |
| MenuControllerTest | ⟨completar⟩ | | | |
| MenuApiControllerTest | ⟨completar⟩ | | | |
| AuthControllerTest | ⟨completar⟩ | | | |
| AdminControllerTest | ⟨completar⟩ | | | |
| InicioControllerTest | ⟨completar⟩ | | | |
| PasswordResetControllerTest | ⟨completar⟩ | | | |
| AuthServiceTest | ⟨completar⟩ | | | |
| CustomUserDetailsServiceTest | ⟨completar⟩ | | | |
| MenuServiceTest | ⟨completar⟩ | | | |
| PasswordResetServiceTest | ⟨completar⟩ | | | |
| ReporteServiceTest | ⟨completar⟩ | | | |
| CompatiblePasswordEncoderTest | ⟨completar⟩ | | | |
| ModelTest | ⟨completar⟩ | | | |
| **Total** | ⟨completar⟩ | | | |

## 4. Cobertura de código — JaCoCo

El `pom.xml` ya genera el reporte de cobertura en `mvn verify` (plugin `jacoco-maven-plugin`,
metas `prepare-agent` y `report`). Abre `target/site/jacoco/index.html` en el navegador y copia
los porcentajes de la fila `Total`:

| Métrica | Cobertura |
|---|---|
| Instrucciones | ⟨completar⟩ % |
| Ramas (branches) | ⟨completar⟩ % |
| Líneas | ⟨completar⟩ % |
| Métodos | ⟨completar⟩ % |
| Clases | ⟨completar⟩ % |

### Cobertura por paquete (los que más importan para este informe)

| Paquete | Cobertura de líneas |
|---|---|
| `Service` (PedidoService, InventarioService, ReporteService, ReporteMultitablaService...) | ⟨completar⟩ % |
| `Controller` (PedidoController, InventarioController, ReporteController...) | ⟨completar⟩ % |
| `Repository` | ⟨completar⟩ % |

> El `pom.xml` no tiene configurado un umbral mínimo (`jacoco:check`), así que el build no falla
> aunque la cobertura sea baja. Si tu institución exige un mínimo (por ejemplo 80 %), avísame y
> agrego la regla — pero solo después de ver el número real, para no romper el build a ciegas.

## 5. Casos de prueba relevantes (verificación funcional)

Esta tabla documenta **qué** se verificó y **por qué**, no solo el conteo. Complétala con el
resultado real (OK / FALLÓ) después de correr `mvn verify`.

| # | Caso de prueba | Objetivo | Resultado |
|---|---|---|---|
| 1 | `entregarDescuentaInventarioYDespachaUnaSolaVez` | El stock se descuenta al pasar a "entregado", sin importar desde dónde se marque | ⟨completar⟩ |
| 2 | `siNoHayStockElPedidoNoCambiaDeEstadoNiSeDespacha` | Si falta stock, el pedido no cambia de estado (transacción atómica) | ⟨completar⟩ |
| 3 | `volverAMarcarEntregadoUnPedidoYaEntregadoNoDuplicaElDescuento` | El descuento de inventario no se duplica | ⟨completar⟩ |
| 4 | `unPedidoEntregadoNoPuedeRetroceder` | Un pedido entregado no puede volver a un estado anterior | ⟨completar⟩ |
| 5 | `guardarRechazaMesaQueNoExiste` | El formulario de pedidos valida que la mesa exista | ⟨completar⟩ |
| 6 | `guardarRechazaPrioridadQueNoCoincideConElEnumDeLaBaseDeDatos` | La prioridad del formulario coincide con el `ENUM` de la base de datos | ⟨completar⟩ |
| 7 | `eliminarInformaCuandoElPedidoTieneRegistrosAsociados` | Un error de base de datos al eliminar se traduce en un mensaje claro, no en una página de error | ⟨completar⟩ |
| 8 | `desactivarMarcaInactivoYQuitaElInsumoDeTodasLasRecetas` | Al eliminar un insumo, se retira también de las recetas que lo usaban | ⟨completar⟩ |
| 9 | `actualizarInsumoRechazaStockQueSuperaElMaximoDeLaColumna` | El stock no puede exceder el límite de la columna `DECIMAL(12,3)` | ⟨completar⟩ |
| 10 | `cadaFiltroInformadoAgregaSuCondicionYSuParametroEnOrden` | Los 8 filtros del reporte multitabla se combinan correctamente en el SQL | ⟨completar⟩ |
| 11 | `unTextoDeFiltroNuncaSeConcatenaAlSqlSiempreVaComoParametro` | Los filtros de texto van como parámetros preparados (no hay inyección SQL) | ⟨completar⟩ |
| 12 | `resumirCuentaCadaPedidoYCadaFacturaUnaSolaVez` | Los totales del reporte no duplican una factura que aparece en varias líneas | ⟨completar⟩ |
| 13 | `escapaCaracteresEspecialesYDescartaCaracteresDeControlInvalidosEnXml` | El Excel generado no se corrompe con tildes, símbolos o caracteres inválidos | ⟨completar⟩ |
| 14 | `multitablaNoConsultaSiElRangoDeFechasEsInvalido` | Un rango de fechas invertido no llega a consultar la base de datos | ⟨completar⟩ |

## 6. Pruebas manuales (integración con MySQL real)

Estas no están automatizadas en `mvn verify` porque requieren una base de datos con datos reales;
se ejecutaron manualmente durante el desarrollo (detalle en `CAMBIOS.md`, sección "Reporte
multitabla"). Repítelas tú para dejar constancia en este informe:

| # | Prueba manual | Cómo hacerla | Resultado |
|---|---|---|---|
| 1 | Consulta multitabla con datos reales | Cargar `sistema.sql`, crear 3-4 pedidos con productos y facturas, filtrar por cada criterio en `/reportes/multitabla` y comparar el número de filas contra una consulta directa en phpMyAdmin | ⟨completar⟩ |
| 2 | Descarga de Excel | Descargar el `.xlsx` desde `/reportes/multitabla/excel` y abrirlo en Excel o LibreOffice | ⟨completar⟩ |
| 3 | Descarga de PDF | Descargar el PDF desde `/reportes/multitabla/pdf` y confirmar que se ve la tabla completa | ⟨completar⟩ |
| 4 | Flujo completo de un pedido | Crear pedido → agregar productos → cocina lo ve con sus productos → marcar entregado → confirmar que el stock bajó | ⟨completar⟩ |

## 7. Defectos encontrados y su estado

| # | Defecto | Dónde se corrigió | Estado |
|---|---|---|---|
| 1 | `sistema.sql` creaba `Menu_Insumo` antes que `Menu` (fallaba la importación) | `src/main/resources/db/sistema.sql` | Corregido |
| 2 | Eliminar/vaciar productos del pedido lanzaba error sin transacción | `Repository/DetallePedidoRepository.java`, `DetallePedidoAdicionRepository.java` | Corregido |
| 3 | La prioridad "alta" del formulario no existía en el `ENUM` de la base de datos | `Controller/PedidoController.java`, `templates/pedidos/nuevo.html` | Corregido |
| 4 | El botón "Actualizar" de un pedido creaba uno nuevo en vez de editar | `Controller/PedidoController.java` | Corregido |
| 5 | El stock solo se descontaba desde una pantalla, no desde el panel de cocina | `Service/PedidoService.java` | Corregido |
| 6 | Sin mensajes de confirmación/error visibles en la interfaz | `templates/fragments/alertas.html`, todas las plantillas | Corregido |

## 8. Conclusiones

⟨Completar después de correr `mvn verify`: si la cobertura y el número de pruebas fallidas son
aceptables para tu rúbrica, o si hace falta añadir más pruebas a un módulo específico.⟩

---

## Cómo obtener cada número (paso a paso)

1. Ejecuta en la raíz del proyecto:
   ```
   mvnw.cmd clean verify
   ```
2. **Pruebas ejecutadas/fallidas:** al final de la consola busca una línea como
   `Tests run: 108, Failures: 0, Errors: 0, Skipped: 0`. Ese es el total de la sección 3.
3. **Desglose por clase:** abre la carpeta `target/surefire-reports/`. Hay un archivo
   `TEST-com.sispe.springboot_web.Service.PedidoServiceTest.xml` (y uno por cada clase) con el
   número exacto de pruebas, fallos y tiempo de esa clase.
4. **Cobertura:** abre `target/site/jacoco/index.html` en el navegador. La tabla de arriba trae el
   resumen total; haciendo clic en cada paquete (`com.sispe.springboot_web.Service`, `...Controller`,
   etc.) se ve el detalle por paquete y por clase.
5. Pega esos números en las tablas de este archivo y marca cada caso de la sección 5 como
   `OK` o `FALLÓ` según lo que haya salido.
