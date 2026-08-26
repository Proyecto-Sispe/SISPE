# Migración de SISPE de PHP a Spring Boot

## 1. Objetivo

Se inició la migración del sistema ubicado en `2do Trimestre/Sistema`, desarrollado en PHP con CodeIgniter, hacia el proyecto Java ubicado en `3er Trimestre/demo`, desarrollado con Spring Boot.

Las decisiones principales fueron:

- Migrar todo el sistema, no solamente un módulo.
- Conservar MySQL y la base de datos existente `sistema`.
- Reemplazar las vistas PHP por vistas Thymeleaf.
- Mantener APIs REST para los módulos que las necesitan.
- Organizar el código usando entidades, repositorios, servicios y controladores Spring.

## 2. Tecnologías utilizadas

El proyecto Spring Boot utiliza:

- Java 17.
- Spring Boot 3.2.4.
- Spring MVC para controladores web.
- Thymeleaf para las vistas HTML.
- Spring Data JPA e Hibernate para el acceso a MySQL.
- Spring Validation para validaciones.
- Spring Security para autenticación y protección de rutas.
- MySQL Connector/J para la conexión con la base de datos.
- Lombok para reducir código repetitivo.
- Spring Boot DevTools para facilitar el desarrollo.
- Maven como administrador de dependencias y compilación.

Las dependencias se encuentran en:

```text
3er Trimestre/demo/pom.xml
```

## 3. Configuración de la base de datos

La configuración se encuentra en:

```text
3er Trimestre/demo/src/main/resources/application.properties
```

La conexión utiliza las variables:

```properties
DB_URL
DB_USERNAME
DB_PASSWORD
```

La intención es conectarse a la base `sistema` existente sin borrar información. Antes de utilizar el sistema en producción se debe confirmar que los nombres de las tablas y columnas coincidan exactamente con el SQL original.

## 4. Estructura de código creada

El código Java está organizado en paquetes:

```text
com.login.demo
├── config
├── controller
├── dto
├── mapper
├── model
├── repository
└── service
```

### `config`

Contiene la configuración de seguridad de Spring, incluyendo el codificador de contraseñas y las reglas de acceso.

Archivo principal:

```text
src/main/java/com/login/demo/config/SecurityConfig.java
```

### `controller`

Contiene los controladores MVC y REST que reciben las solicitudes del navegador o de clientes externos.

Controladores migrados o iniciados:

- `AuthController`: login, logout y dashboard.
- `RegistroController`: registro de nuevos usuarios.
- `UsuarioController`: administración de usuarios.
- `MenuController`: gestión web del menú.
- `MenuApiController`: API REST del menú.
- `MesaController`: gestión de mesas.
- `PedidoApiController`: API REST de pedidos.
- `CocinaController`: administración de pedidos en cocina.
- `FacturaController`: consulta de facturas.
- `ReporteController`: reportes y resumen del sistema.

### `model`

Contiene las entidades JPA que representan las tablas de MySQL:

- `Usuario`.
- `UsuarioId` para la clave compuesta de la persona.
- `Categoria`.
- `Menu`.
- `Mesa`.
- `Pedido`.
- `Factura`.
- `PasswordReset`.

La entidad `Usuario` fue adaptada para representar la tabla `Persona` y sus campos originales, entre ellos nombres, apellidos, teléfono, correo, contraseña y estado.

### `repository`

Contiene interfaces Spring Data JPA para consultar y guardar información:

- `UsuarioRepository`.
- `MenuRepository`.
- `MesaRepository`.
- `PedidoRepository`.
- `FacturaRepository`.
- `PasswordResetRepository`.

### `service`

Contiene la lógica de negocio separada de los controladores. Se inició la migración del servicio de usuarios y se creó el servicio del menú.

### `dto` y `mapper`

Se utilizan para separar los datos recibidos desde formularios o APIs de las entidades internas de la base de datos. `UsuarioMapper` convierte entre la entidad `Usuario` y su DTO.

## 5. Módulos migrados

### Autenticación

Se agregó un flujo inicial de:

1. Mostrar el formulario de login en `/login`.
2. Recibir correo y contraseña.
3. Buscar el usuario activo en MySQL.
4. Validar la contraseña.
5. Crear una sesión HTTP.
6. Redirigir al dashboard.
7. Cerrar sesión mediante `/logout`.

También se configuró `PasswordEncoder` para permitir contraseñas codificadas de forma segura.

> Nota: si las contraseñas existentes en MySQL están guardadas en texto plano o con otro algoritmo, se debe definir una estrategia de compatibilidad y actualización progresiva.

### Registro de usuarios

Se creó la ruta `/registro` y una vista Thymeleaf para registrar usuarios. El controlador valida datos básicos, comprueba que el correo no esté repetido y guarda la nueva persona.

### Usuarios/personas

La entidad de usuarios se relacionó con la tabla `Persona` del esquema PHP. Se incorporó una clave compuesta mediante `UsuarioId`, debido a que la tabla utiliza `id_usuario` junto con `pkfk_Tipo_doc`.

### Menú y categorías

Se añadieron entidades, repositorio, servicio, controlador MVC y API REST para el menú. La interfaz permite listar productos y realizar operaciones administrativas básicas.

### Mesas

Se creó la entidad `Mesa`, su repositorio y el controlador web para listar, crear y eliminar mesas.

### Pedidos

Se añadió la entidad `Pedido`, el repositorio y la API REST `/api/pedidos`. El modelo contempla información del cliente, mesa, estado y total.

### Cocina

Se creó el panel `/cocina` para consultar pedidos activos y actualizar estados como:

- Pendiente.
- En preparación.
- En camino.
- Entregado.

### Facturación

Se creó la entidad `Factura`, el repositorio y el controlador `/facturas` para consultar información de facturación.

### Reportes

Se creó el controlador `/reportes` y una vista para mostrar resúmenes de ventas, facturas, pedidos y pedidos recientes.

### Recuperación de contraseña

Se creó la entidad `PasswordReset` y su repositorio como base para implementar tokens de recuperación. El envío de correo y la pantalla final de cambio de contraseña todavía requieren completar la integración.

## 6. Vistas Thymeleaf creadas

Las vistas están en:

```text
src/main/resources/templates
```

Se crearon o adaptaron:

- `login.html`.
- `registro.html`.
- `dashboard.html`.
- `usuarios/usuario.html`.
- `menu/index.html`.
- `mesas/index.html`.
- `cocina/index.html`.
- `facturas/index.html`.
- `reportes/index.html`.

Los recursos CSS se encuentran en:

```text
src/main/resources/static/css/sispe.css
```

El estilo incluye navegación administrativa, formularios, tablas, tarjetas, estados de pedidos, mensajes de error y mensajes de éxito.

## 7. Clases eliminadas

Se eliminaron clases de prueba o duplicadas que no formaban parte de una arquitectura Spring válida:

- `model/Entity.java`.
- `model/Table.java`.
- `model/edad.java`.
- `controller/usuarioService.java`.

Estas clases podían generar confusión o conflictos con las anotaciones y servicios reales.

## 8. Equivalencia PHP → Spring Boot

| PHP/CodeIgniter | Spring Boot |
|---|---|
| `Controllers` | `controller` |
| `Models` | `model`, `repository` y `service` |
| `Views` | `resources/templates` |
| Rutas de CodeIgniter | `@GetMapping`, `@PostMapping`, `@RequestMapping` |
| Consultas del modelo | Métodos de `JpaRepository` |
| Sesiones PHP | Sesión HTTP y Spring Security |
| Validación de formularios | Spring Validation |
| Archivos CSS/JS públicos | `resources/static` |

## 9. Estado actual

La migración tiene una base funcional para:

- Estructura Spring Boot.
- Conexión configurable a MySQL.
- Usuarios y autenticación inicial.
- Registro.
- Menú.
- Mesas.
- Pedidos.
- Cocina.
- Facturas.
- Reportes.
- Recuperación de contraseña como estructura inicial.

## 10. Cumplimiento de la rúbrica técnica

### 10.1 Arquitectura Java y memoria JVM

La solución usa separación por capas: controladores, servicios, repositorios y entidades. En ejecución, la JVM administra objetos JPA y sesiones en el Heap; las variables locales y referencias de llamadas se mantienen en el Stack. Hibernate gestiona el ciclo de vida de las entidades mediante los estados transient, managed, detached y removed dentro del contexto de persistencia.

### 10.2 Autenticación y roles

El login identifica al usuario activo y asigna dinámicamente un rol de sesión según el tipo de documento: ADMIN, COCINA, CAJERO o CLIENTE. Las rutas públicas son login, registro y recursos estáticos; las demás operaciones se ejecutan dentro del flujo autenticado. Como mejora de endurecimiento, la autorización por método debe completarse con `@PreAuthorize` cuando el catálogo definitivo de roles del SQL sea confirmado.

### 10.3 CRUD y validaciones

Los formularios y endpoints usan validación declarativa de Spring Validation, incluyendo `@NotNull`, `@NotBlank`, `@Email` y `@Size`. También se validan reglas de negocio como correo único, usuario activo y estados permitidos para pedidos. Los errores deben presentarse al usuario sin exponer detalles internos de la base de datos.

### 10.4 Reportes y filtros multicriterio

El módulo `/reportes` permite combinar filtros por estado del pedido y usuario mediante parámetros `estado` y `usuario`. Los resultados filtrados se reflejan en la tabla y los indicadores de pedidos; el resumen de ventas y facturas se calcula desde los datos persistidos.

## 11. Calidad, métricas y mejora continua

### 11.1 Documento comparativo

| Criterio | PHP/CodeIgniter | Spring Boot | Resultado |
|---|---|---|---|
| Arquitectura | MVC con lógica mezclada en modelos | Capas y dependencias explícitas | Mayor mantenibilidad |
| Persistencia | Consultas manuales | JPA/Hibernate y repositorios | Menos código repetitivo |
| Seguridad | Sesiones y validación manual | Spring Security y BCrypt | Mejor control centralizado |
| Vistas | PHP embebido | Thymeleaf | Separación más clara |
| Pruebas | Limitadas | Starter de pruebas y perfiles | Base preparada para QA |

### 11.2 Matriz de métricas

| Métrica | Objetivo | Evidencia | Frecuencia |
|---|---|---|---|
| Cobertura de pruebas | ≥ 70% | Reporte JaCoCo | Cada entrega |
| Errores críticos | 0 abiertos | Registro de incidencias | Antes de publicar |
| Tiempo de respuesta CRUD | < 2 s | Prueba de integración | Por versión |
| Validación de formularios | 100% de entradas críticas | Casos negativos | Cada cambio |
| Disponibilidad | ≥ 99% en operación | Monitoreo | Mensual |

### 11.3 Plan de gestión de calidad

1. Revisar código y nombres de tablas antes de integrar.
2. Ejecutar pruebas unitarias de servicios y validadores.
3. Ejecutar pruebas de integración contra una base MySQL de prueba.
4. Revisar autorización, contraseñas, CSRF y datos sensibles.
5. Registrar defectos con severidad, responsable, evidencia y corrección.
6. Aprobar una versión solo cuando los defectos críticos estén cerrados.

### 11.4 Informe de verificación y validación QA

- **Verificación:** la estructura de paquetes, entidades, repositorios, controladores y vistas corresponde al diseño definido.
- **Validación funcional:** se deben comprobar registro, login, menú, mesas, pedidos, cocina, facturas, reportes y recuperación de contraseña con datos reales de prueba.
- **Casos mínimos:** credenciales inválidas, correo duplicado, campos vacíos, correo incorrecto, estado de pedido no permitido, filtro combinado y acceso sin sesión.
- **Criterio de aceptación:** respuesta correcta, mensaje comprensible, persistencia confirmada y ausencia de exposición de contraseñas.

### 11.5 Propuesta de mejora continua PDCA

- **Plan:** priorizar autorización por rol, cobertura de pruebas y compatibilidad completa con el SQL.
- **Do:** implementar cambios en una rama de trabajo y ejecutar pruebas automatizadas.
- **Check:** comparar métricas contra la matriz, revisar incidencias y realizar pruebas de aceptación.
- **Act:** corregir desviaciones, documentar la lección aprendida y actualizar el estándar para la siguiente iteración.

## 12. Pendientes importantes

Antes de considerar terminada la migración se deben completar estas tareas:

1. Comparar todas las entidades JPA con el archivo SQL real de `sistema`.
2. Confirmar nombres exactos de tablas, columnas, claves y relaciones.
3. Completar el detalle de pedidos y la relación entre pedidos y productos.
4. Completar roles y permisos de administrador, cocina, cajero y cliente.
5. Completar el cambio de estado de mesas y pedidos.
6. Completar el proceso de recuperación de contraseña con tokens y correo.
7. Añadir validaciones con `@Valid`, `@NotBlank`, `@Email` y reglas de negocio.
8. Crear pruebas unitarias e integración.
9. Instalar Java 17 y Maven en el equipo de ejecución.
10. Probar la aplicación conectada a MySQL con datos controlados.
11. Revisar protección CSRF, manejo de errores y autorización por endpoint.
12. Migrar JavaScript, imágenes y cualquier vista PHP que aún no tenga equivalente.

## 11. Ejecución del proyecto

Desde la carpeta del proyecto Spring Boot:

```bash
cd "3er Trimestre/demo"
```

Configurar las variables de conexión a MySQL y ejecutar:

```bash
./mvnw spring-boot:run
```

En Windows puede utilizarse:

```bash
mvnw.cmd spring-boot:run
```

El entorno donde se realizaron los cambios no tenía Java configurado, por lo que la compilación final debe realizarse en un equipo con Java 17 y Maven Wrapper disponibles.

## 12. Conclusión

Se inició una migración incremental desde CodeIgniter PHP hacia Spring Boot manteniendo la base MySQL y trasladando la interfaz a Thymeleaf. La nueva estructura separa correctamente entidades, repositorios, servicios, controladores y vistas, lo que facilita continuar con los módulos restantes y realizar pruebas de forma ordenada.

La migración todavía debe validarse contra el esquema real de MySQL y completarse en los flujos de detalle de pedidos, permisos, recuperación de contraseña y pruebas de integración.
