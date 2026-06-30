<?php

use CodeIgniter\Router\RouteCollection;

/**
 * @var RouteCollection $routes
 */

$routes->get('/', 'InicioController::index');
$routes->get('login', 'LoginController::index');
$routes->post('login', 'LoginController::login');
$routes->get('dashboard', 'LoginController::dashboard');
$routes->get('logout', 'LoginController::logout');
$routes->get('registro', 'RegistroController::registrar');
$routes->post('guardar', 'RegistroController::guardar');

// Recuperacion de contrasena (vistas web)
$routes->get('olvide-password', 'PasswordController::olvide');
$routes->post('olvide-password', 'PasswordController::enviarEnlace');
$routes->get('reset-password', 'PasswordController::reset');
$routes->post('reset-password', 'PasswordController::actualizar');

$routes->get('personas', 'AdminPersonaController::index');                     // Lista y Filtros
$routes->get('personas/crear', 'AdminPersonaController::crear');               // Vista Formulario Agregar
$routes->post('personas/guardar', 'AdminPersonaController::guardar');           // Procesar nuevo
$routes->get('personas/editar/(:num)/(:num)', 'AdminPersonaController::editar/$1/$2'); // Vista Formulario Editar (Pasa ID y TipoDoc)
$routes->post('personas/actualizar', 'AdminPersonaController::actualizar');     // Procesar Cambios
$routes->get('personas/eliminar/(:num)/(:num)', 'AdminPersonaController::eliminar/$1/$2'); // Acción Eliminar (Pasa ID y TipoDoc)


$routes->get('facturas', 'FacturaController::index');

// 1. Panel principal que muestra el Grid de simulación (Tu Mesas 2.Html)
$routes->get('mesas', 'Mesas::index');

// 2. Pantalla con el formulario para registrar mesas (Tu Agregar Mesa.Html)
$routes->get('mesas/agregar', 'Mesas::agregar');

// 3. Destino del formulario que procesa el insert en MySQL
$routes->post('mesas/guardar', 'Mesas::guardar');

// 1. La URL exacta que lee el celular al escanear el QR permanente de la mesa
$routes->get('cliente/escanear/(:num)', 'ClienteQR::escanear/$1');

// 2. Destino del formulario especial que procesa el Nombre, Cédula y abre el Pedido
$routes->post('cliente/registrar_acceso', 'ClienteQR::registrarAcceso');

// 3. Formulario de Pedidos para el Cliente (Tu Formulario Menu.Html)
$routes->get('cliente/pedido', 'ClienteQR::pantallaPedido');

// 4. Guarda el pedido y las observaciones/adiciones del menú en la base de datos
$routes->post('cliente/guardar_pedido', 'ClienteQR::guardarPedido');

// 5. Estado actual del pedido del cliente (Muestra el reporte del Cocinero)
$routes->get('cliente/estado', 'ClienteQR::verEstado');

// Rutas nuevas para Editar y Actualizar
$routes->get('mesas/editar/(:num)', 'Mesas::editar/$1');
$routes->post('mesas/actualizar', 'Mesas::actualizar');

// Ruta nueva para Eliminar
$routes->get('tables/delete/(:num)', 'Tables::delete/$1');

// Link to the "Orders" button on your menu that loads the kitchen view
$routes->get('pedidos', 'Cocina::index');

// Ruta interna para procesar el cambio de los estados semáforo
$routes->get('cocina/cambiarestado/(:num)/(:any)', 'Cocina::cambiarEstado/$1/$2');

// --- BILLING AND CASH MODULE ---
// 1. Carga el historial general (panel_facturas.php)
$routes->get('facturas', 'FacturaController::index');

// 2. Carga la tirilla de pago individual e impresión (ver_factura.php)
$routes->get('factura/ver/(:num)', 'FacturaController::ver/$1');

// 3. Procesa la eliminación física de la factura tras ser impresa
$routes->get('invoices/delete/(:num)', 'InvoiceController::delete/$1');

// routes for PDF reports
$routes->get('reportes', 'ReporteController::index');
$routes->get('reportes/generar', 'ReporteController::generar'); // Consultas multitabla -> PDF directo
$routes->get('reportes/pdf', 'ReporteController::pdfVentas');
$routes->get('reportes/productos', 'ReporteController::pdfProductos');
$routes->get('reportes/usuarios', 'ReporteController::pdfUsuarios');


// Carga la tirilla de pago mediante método GET
$routes->get('factura/ver/(:num)', 'FacturaController::ver/$1');

// Procesa la eliminación mediante formulario seguro POST
$routes->post('facturas/eliminar', 'FacturaController::eliminar');

// Rutas del CRUD del Menú (Admin)
$routes->get('gestion-menu', 'MenuController::index');
$routes->post('menu/guardar', 'MenuController::guardar');
$routes->get('menu/eliminar/(:any)', 'MenuController::eliminar/$1');

// Ruta del Menú Digital (Cliente)
$routes->get('menu_digital', 'MenuController::digital');

$routes->post('menu/guardarCategoria', 'MenuController::guardarCategoria');

/*
|--------------------------------------------------------------------------
| API REST (para consumir desde Postman)
|--------------------------------------------------------------------------
|
| Ejemplos:
|   POST   /api/login
|   GET    /api/mesas        GET /api/mesas/1
|   POST   /api/mesas        PUT /api/mesas/1    
|   DELETE /api/mesas/1
|   (igual para personas, menu, pedidos, facturas)
*/
$routes->group('api', ['namespace' => 'App\Controllers\Api', 'filter' => 'cors'], static function ($routes) {
    // Autenticacion
    $routes->post('login', 'AuthApi::login');

    // Recuperacion de contrasena
    $routes->post('forgot-password', 'AuthApi::forgotPassword');
    $routes->post('reset-password', 'AuthApi::resetPassword');

    // Recursos CRUD
    $routes->resource('mesas',    ['controller' => 'MesaApi']);
    $routes->resource('menu',     ['controller' => 'MenuApi']);
    $routes->resource('pedidos',  ['controller' => 'PedidoApi']);
    $routes->resource('facturas', ['controller' => 'FacturaApi']);
    $routes->resource('personas', ['controller' => 'PersonaApi']);
});
