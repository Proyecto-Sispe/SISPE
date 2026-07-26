# Backlog Scrum - Proyecto SISPE

Sistema de gestión para restaurante (CodeIgniter 4 + API REST + App Android Kotlin).
Este documento está pensado para cargarse en **Zenhub**.

## Equipo

| Integrante | Rol            | Enfoque sugerido                          |
| ---------- | -------------- | ----------------------------------------- |
| Victor     | Scrum Master   | Facilita ceremonias, quita bloqueos, gestiona el tablero y también apoya desarrollo |
| Adrian     | Desarrollador  | Backend / API (CodeIgniter)               |
| Juan       | Desarrollador  | Frontend web (Vistas CI4)                 |
| Jerson     | Desarrollador  | App Android (Kotlin)                      |

## Configuración recomendada en Zenhub

**Pipelines (columnas del tablero):**
1. New Issues (recién creadas)
2. Product Backlog
3. Sprint Backlog
4. In Progress
5. Review / QA
6. Done

**Sprints:** duración de 2 semanas (según la metodología acordada en las guías).

**Story Points (escala Fibonacci):** 1, 2, 3, 5, 8. Estimen en Planning Poker en cada Sprint Planning.

**Labels sugeridas:** `backend`, `frontend-web`, `android`, `base-de-datos`, `api`, `bug`, `documentacion`, `qa`.

**Epics en Zenhub:** cada uno de los bloques de abajo (E1...E8) se crea como un *Epic* y las historias/tareas se enlazan a él.

---

## E1 - Configuración e Infraestructura (Sprint 1)

| # | Issue (Historia / Tarea)                                              | Label(s)            | Puntos | Responsable |
| - | --------------------------------------------------------------------- | ------------------- | ------ | ----------- |
| 1 | Configurar repositorio Git y flujo de ramas (main/develop/feature)    | documentacion       | 2      | Victor      |
| 2 | Definir Product Backlog inicial y priorizar en Zenhub                 | documentacion       | 3      | Victor      |
| 3 | Crear base de datos y ejecutar script SQL de tablas base              | base-de-datos       | 3      | Adrian      |
| 4 | Configurar conexión a BD y variables de entorno (.env) en CodeIgniter | backend             | 2      | Adrian      |
| 5 | Configurar proyecto Android base y cliente Retrofit                   | android             | 3      | Jerson      |
| 6 | Definir estándar de código y estructura de carpetas                   | documentacion       | 1      | Juan        |

## E2 - Autenticación y Usuarios (Sprint 1-2)

| # | Issue (Historia / Tarea)                                             | Label(s)          | Puntos | Responsable |
| - | -------------------------------------------------------------------- | ----------------- | ------ | ----------- |
| 1 | Como usuario quiero iniciar sesión con correo y contraseña           | backend, api      | 5      | Adrian      |
| 2 | Como usuario quiero registrarme en el sistema                        | backend           | 3      | Adrian      |
| 3 | Recuperación / restablecimiento de contraseña                        | backend           | 3      | Adrian      |
| 4 | Vista web de login y registro                                        | frontend-web      | 3      | Juan        |
| 5 | Pantalla de login en la app Android (consumo de API Auth)            | android           | 5      | Jerson      |
| 6 | Control de acceso por roles (admin / mesero / cocina / cliente)      | backend           | 5      | Adrian      |

## E3 - Gestión de Personas (Sprint 2)

| # | Issue (Historia / Tarea)                                     | Label(s)      | Puntos | Responsable |
| - | ------------------------------------------------------------ | ------------- | ------ | ----------- |
| 1 | CRUD de personas en backend (modelo + controlador)           | backend       | 5      | Adrian      |
| 2 | Endpoints API de personas                                    | api           | 3      | Adrian      |
| 3 | Vista web para listar/agregar/editar personas               | frontend-web  | 3      | Juan        |
| 4 | Pantalla Android CRUD de personas                            | android       | 5      | Jerson      |

## E4 - Gestión de Productos y Menú (Sprint 2-3)

| # | Issue (Historia / Tarea)                              | Label(s)      | Puntos | Responsable |
| - | ----------------------------------------------------- | ------------- | ------ | ----------- |
| 1 | CRUD de productos (backend + API)                     | backend, api  | 5      | Adrian      |
| 2 | Gestión de menú y categorías                          | backend       | 5      | Adrian      |
| 3 | Vista web de productos y menú                         | frontend-web  | 5      | Juan        |
| 4 | Pantalla Android de menú/productos                    | android       | 5      | Jerson      |

## E5 - Gestión de Mesas y Pedidos (Sprint 3-4)

| # | Issue (Historia / Tarea)                                       | Label(s)      | Puntos | Responsable |
| - | -------------------------------------------------------------- | ------------- | ------ | ----------- |
| 1 | CRUD de mesas y estados (libre/ocupada)                        | backend, api  | 5      | Adrian      |
| 2 | Crear y gestionar pedidos asociados a mesa                     | backend, api  | 8      | Adrian      |
| 3 | Vista web de mesas y toma de pedidos                           | frontend-web  | 8      | Juan        |
| 4 | Pantalla Android de mesas y pedidos                            | android       | 8      | Jerson      |
| 5 | Módulo de cocina: ver pedidos entrantes en tiempo real         | frontend-web  | 5      | Juan        |

## E6 - Pedido por QR del Cliente (Sprint 4)

| # | Issue (Historia / Tarea)                               | Label(s)          | Puntos | Responsable |
| - | ------------------------------------------------------ | ----------------- | ------ | ----------- |
| 1 | Generar código QR por mesa                             | backend           | 3      | Adrian      |
| 2 | Vista pública para que el cliente ordene desde el QR   | frontend-web      | 8      | Juan        |
| 3 | Confirmación de pedido y pantalla de "gracias"         | frontend-web      | 2      | Juan        |

## E7 - Facturación y Reportes (Sprint 5)

| # | Issue (Historia / Tarea)                                   | Label(s)      | Puntos | Responsable |
| - | ---------------------------------------------------------- | ------------- | ------ | ----------- |
| 1 | Generar factura a partir de un pedido                      | backend, api  | 5      | Adrian      |
| 2 | Vista web de facturas y detalle                            | frontend-web  | 5      | Juan        |
| 3 | Reportes de ventas / pedidos / estadísticas                | backend       | 5      | Adrian      |
| 4 | Vista web de reportes (tablas/gráficos)                    | frontend-web  | 5      | Juan        |
| 5 | Consulta de facturas/reportes desde la app Android         | android       | 5      | Jerson      |

## E8 - Pruebas, Integración y Entrega (Sprint 5-6)

| # | Issue (Historia / Tarea)                                     | Label(s)          | Puntos | Responsable |
| - | ------------------------------------------------------------ | ----------------- | ------ | ----------- |
| 1 | Pruebas de integración API web <-> Android                   | qa, api           | 5      | Jerson      |
| 2 | Pruebas funcionales de cada módulo                           | qa                | 5      | Todos       |
| 3 | Corrección de bugs detectados                                | bug               | 5      | Adrian/Juan |
| 4 | Manual de usuario y documentación técnica                    | documentacion     | 3      | Victor      |
| 5 | Despliegue final y capacitación                              | documentacion     | 3      | Victor      |

---

## Ceremonias Scrum (a cargo de Victor)

- **Sprint Planning:** inicio de cada sprint, se estiman y asignan las issues.
- **Daily Standup:** breve, diario (¿qué hice? ¿qué haré? ¿qué me bloquea?).
- **Sprint Review:** fin de sprint, se muestra el incremento funcional.
- **Sprint Retrospective:** fin de sprint, mejoras del equipo.

## Tips para cargarlo en Zenhub

1. Crea los **Epics** E1...E8.
2. Convierte cada fila de las tablas en un **Issue** y enlázalo a su Epic.
3. Asigna **Story Points** y **Assignee** en cada issue.
4. Crea los **Sprints** (2 semanas) y arrastra las issues al sprint que corresponde.
5. Usa el **tablero (board)** para mover issues entre pipelines.
