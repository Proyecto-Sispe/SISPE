<?php

namespace App\Controllers;

use App\Controllers\BaseController;
use App\Models\AdminPersonaModel;
use App\Models\FacturaModel;
use App\Models\MenuModel;
use App\Models\ReporteModel;
use Dompdf\Dompdf;
use Dompdf\Options;

class ReporteController extends BaseController
{
      /**
     * Catalogo central de reportes multitabla disponibles.
     * Cada entrada define el metodo del modelo a ejecutar, el titulo,
     * las columnas (label/key/formato) y la columna a totalizar (si aplica).
     */
    private function definiciones(): array
    {
        return [
            'ventas_detalladas' => [
                'titulo'   => 'Reporte de Ventas Detalladas',
                'metodo'   => 'ventasDetalladas',
                'grupo'    => 'Ventas',
                'icono'    => '&#128176;',
                'desc'     => 'Facturas cruzadas con pedido, mesa, cliente y metodos de pago.',
                'usaFechas'=> true,
                'totalKey' => 'Total',
                'columnas' => [
                    ['label' => 'ID Factura',      'key' => 'id_factura'],
                    ['label' => 'Pedido',          'key' => 'id_pedido'],
                    ['label' => 'Mesa',            'key' => 'id_mesa'],
                    ['label' => 'Cliente',         'key' => 'nombre_cliente'],
                    ['label' => 'Estado',          'key' => 'estado_pedido'],
                    ['label' => 'Fecha',           'key' => 'Fecha_hora', 'formato' => 'fecha'],
                    ['label' => 'Metodos de pago', 'key' => 'metodos_pago'],
                    ['label' => 'Total',           'key' => 'Total',      'formato' => 'money'],
                ],
            ],
            'ventas_item' => [
                'titulo'   => 'Reporte de Ventas por Producto (Item por Item)',
                'metodo'   => 'ventasPorItem',
                'grupo'    => 'Ventas',
                'icono'    => '&#129534;',
                'desc'     => 'Cada producto vendido con su pedido, categoria, cantidad y subtotal.',
                'usaFechas'=> true,
                'totalKey' => 'subtotal',
                'columnas' => [
                    ['label' => 'Pedido',    'key' => 'id_pedido'],
                    ['label' => 'Producto',  'key' => 'Productos'],
                    ['label' => 'Categoria', 'key' => 'nom_categoria'],
                    ['label' => 'Cantidad',  'key' => 'cantidad'],
                    ['label' => 'Valor Unit.', 'key' => 'valor_venta', 'formato' => 'money'],
                    ['label' => 'Subtotal',  'key' => 'subtotal',  'formato' => 'money'],
                    ['label' => 'Fecha',     'key' => 'fecha_pedido', 'formato' => 'fecha'],
                ],
            ],
            'productos_vendidos' => [
                'titulo'   => 'Reporte de Productos Mas Vendidos',
                'metodo'   => 'productosVendidos',
                'grupo'    => 'Ventas',
                'icono'    => '&#127869;',
                'desc'     => 'Ranking de productos por unidades vendidas e ingresos generados.',
                'usaFechas'=> true,
                'totalKey' => 'total',
                'columnas' => [
                    ['label' => 'Producto',  'key' => 'Productos'],
                    ['label' => 'Categoria', 'key' => 'nom_categoria'],
                    ['label' => 'Unidades',  'key' => 'unidades'],
                    ['label' => 'Ingresos',  'key' => 'total', 'formato' => 'money'],
                ],
            ],
            'ventas_categoria' => [
                'titulo'   => 'Reporte de Ventas por Categoria',
                'metodo'   => 'ventasPorCategoria',
                'grupo'    => 'Ventas',
                'icono'    => '&#128202;',
                'desc'     => 'Totales de venta agrupados por cada categoria del menu.',
                'usaFechas'=> true,
                'totalKey' => 'total',
                'columnas' => [
                    ['label' => 'Categoria', 'key' => 'nom_categoria'],
                    ['label' => 'Unidades',  'key' => 'unidades'],
                    ['label' => 'Ingresos',  'key' => 'total', 'formato' => 'money'],
                ],
            ],
            'ventas_metodo_pago' => [
                'titulo'   => 'Reporte de Ventas por Metodo de Pago',
                'metodo'   => 'ventasPorMetodoPago',
                'grupo'    => 'Ventas',
                'icono'    => '&#128179;',
                'desc'     => 'Transacciones y montos recaudados por cada metodo de pago.',
                'usaFechas'=> true,
                'totalKey' => 'total',
                'columnas' => [
                    ['label' => 'Metodo de pago', 'key' => 'Tipo_pago'],
                    ['label' => 'Transacciones',  'key' => 'transacciones'],
                    ['label' => 'Monto total',    'key' => 'total', 'formato' => 'money'],
                ],
            ],
            'pedidos_estado' => [
                'titulo'   => 'Reporte de Pedidos por Estado',
                'metodo'   => 'pedidosPorEstado',
                'grupo'    => 'Operacion',
                'icono'    => '&#128221;',
                'desc'     => 'Cantidad de pedidos agrupados por su estado actual.',
                'usaFechas'=> true,
                'totalKey' => null,
                'columnas' => [
                    ['label' => 'Estado',   'key' => 'estado'],
                    ['label' => 'Cantidad', 'key' => 'cantidad'],
                ],
            ],
            'pedidos_mesa' => [
                'titulo'   => 'Reporte de Pedidos por Mesa',
                'metodo'   => 'pedidosPorMesa',
                'grupo'    => 'Operacion',
                'icono'    => '&#127869;',
                'desc'     => 'Listado de pedidos con su mesa, ubicacion, cliente y prioridad.',
                'usaFechas'=> true,
                'totalKey' => null,
                'columnas' => [
                    ['label' => 'Pedido',    'key' => 'id_pedido'],
                    ['label' => 'Mesa',      'key' => 'id_mesa'],
                    ['label' => 'Ubicacion', 'key' => 'Ubicacion'],
                    ['label' => 'Cliente',   'key' => 'nombre_cliente'],
                    ['label' => 'Estado',    'key' => 'estado'],
                    ['label' => 'Prioridad', 'key' => 'prioridad'],
                    ['label' => 'Fecha',     'key' => 'fecha_pedido', 'formato' => 'fecha'],
                ],
            ],
            'ocupacion_mesas' => [
                'titulo'   => 'Reporte de Ocupacion de Mesas',
                'metodo'   => 'ocupacionMesas',
                'grupo'    => 'Operacion',
                'icono'    => '&#127869;',
                'desc'     => 'Mesas con su capacidad, estado y total de pedidos historicos.',
                'usaFechas'=> false,
                'totalKey' => null,
                'columnas' => [
                    ['label' => 'Mesa',          'key' => 'id_Mesa'],
                    ['label' => 'Capacidad',     'key' => 'Capacidad'],
                    ['label' => 'Ubicacion',     'key' => 'Ubicacion'],
                    ['label' => 'Estado',        'key' => 'Estado', 'formato' => 'estadoMesa'],
                    ['label' => 'Total pedidos', 'key' => 'total_pedidos'],
                ],
            ],
            'sesiones_clientes' => [
                'titulo'   => 'Reporte de Sesiones de Clientes (QR)',
                'metodo'   => 'sesionesClientes',
                'grupo'    => 'Operacion',
                'icono'    => '&#128241;',
                'desc'     => 'Sesiones creadas por escaneo de QR con su mesa y vigencia.',
                'usaFechas'=> true,
                'totalKey' => null,
                'columnas' => [
                    ['label' => 'Sesion',     'key' => 'id_sesion'],
                    ['label' => 'Cliente',    'key' => 'nombre_cliente'],
                    ['label' => 'Cedula',     'key' => 'cedula_cliente'],
                    ['label' => 'Mesa',       'key' => 'id_mesa'],
                    ['label' => 'Ubicacion',  'key' => 'Ubicacion'],
                    ['label' => 'Inicio',     'key' => 'fecha_inicio', 'formato' => 'fecha'],
                    ['label' => 'Fin',        'key' => 'fecha_fin',    'formato' => 'fecha'],
                    ['label' => 'Activa',     'key' => 'activa', 'formato' => 'siNo'],
                ],
            ],
            'usuarios_rol' => [
                'titulo'   => 'Reporte de Usuarios por Rol',
                'metodo'   => 'usuariosPorRol',
                'grupo'    => 'Administracion',
                'icono'    => '&#128101;',
                'desc'     => 'Personas activas con su tipo de documento, contacto y rol asignado.',
                'usaFechas'=> false,
                'totalKey' => null,
                'columnas' => [
                    ['label' => 'Documento', 'key' => 'id_usuario'],
                    ['label' => 'Tipo doc.', 'key' => 'tipo_doc'],
                    ['label' => 'Nombre',    'key' => 'nombre'],
                    ['label' => 'Correo',    'key' => 'Correo_usu'],
                    ['label' => 'Telefono',  'key' => 'Telefono'],
                    ['label' => 'Rol',       'key' => 'Nom_rol'],
                ],
            ],
            'menu_categoria' => [
                'titulo'   => 'Reporte de Menu por Categoria',
                'metodo'   => 'menuPorCategoria',
                'grupo'    => 'Administracion',
                'icono'    => '&#128214;',
                'desc'     => 'Catalogo completo de productos del menu agrupados por categoria.',
                'usaFechas'=> false,
                'totalKey' => null,
                'columnas' => [
                    ['label' => 'ID',          'key' => 'id_menu'],
                    ['label' => 'Producto',    'key' => 'Productos'],
                    ['label' => 'Categoria',   'key' => 'nom_categoria'],
                    ['label' => 'Precio',      'key' => 'Precio', 'formato' => 'money'],
                    ['label' => 'Descripcion', 'key' => 'descripcion'],
                ],
            ],
            'detalle_pedidos' => [
                'titulo'   => 'Reporte Detallado de Pedidos',
                'metodo'   => 'detallePedidosCompleto',
                'grupo'    => 'Operacion',
                'icono'    => '&#128203;',
                'desc'     => 'Desglose de cada pedido con sus productos, mesa, estado y subtotal.',
                'usaFechas'=> true,
                'totalKey' => 'subtotal',
                'columnas' => [
                    ['label' => 'Pedido',    'key' => 'id_pedido'],
                    ['label' => 'Mesa',      'key' => 'id_mesa'],
                    ['label' => 'Ubicacion', 'key' => 'Ubicacion'],
                    ['label' => 'Producto',  'key' => 'Productos'],
                    ['label' => 'Cant.',     'key' => 'cantidad'],
                    ['label' => 'Valor',     'key' => 'valor_venta', 'formato' => 'money'],
                    ['label' => 'Subtotal',  'key' => 'subtotal',  'formato' => 'money'],
                    ['label' => 'Estado',    'key' => 'estado'],
                    ['label' => 'Fecha',     'key' => 'fecha_pedido', 'formato' => 'fecha'],
                ],
            ],
            'resumen_general' => [
                'titulo'   => 'Resumen General del Sistema',
                'metodo'   => 'resumenGeneral',
                'grupo'    => 'Administracion',
                'icono'    => '&#128200;',
                'desc'     => 'Indicadores clave (KPIs) consolidados de todo el restaurante.',
                'usaFechas'=> false,
                'totalKey' => null,
                'columnas' => [
                    ['label' => 'Indicador', 'key' => 'indicador'],
                    ['label' => 'Valor',     'key' => 'valor', 'formato' => 'auto'],
                ],
            ],
        ];
    }
    public function index()
    {
        if (session('rol') !== 'Administrador') {
            return redirect()->to('dashboard')->with('error', 'Acceso denegado');
        }

        return view('reportes/index', [
            'reportes' => $this->definiciones(),
        ]);
    }

    /**
     * Punto unico de generacion: recibe ?tipo=...&desde=...&hasta=...
     * Ejecuta la consulta multitabla y envia el resultado directo al PDF.
     */
    public function generar()
    {
        if (session('rol') !== 'Administrador') {
            return redirect()->to('dashboard')->with('error', 'Acceso denegado');
        }

        $tipo  = $this->request->getGet('tipo');
        $desde = $this->request->getGet('desde');
        $hasta = $this->request->getGet('hasta');

        $defs = $this->definiciones();
        if (empty($tipo) || !isset($defs[$tipo])) {
            return redirect()->to('reportes')->with('error', 'El reporte solicitado no es valido.');
        }

        $def    = $defs[$tipo];
        $metodo = $def['metodo'];

        $model = new ReporteModel();
        $filas = $model->$metodo($desde, $hasta);

        // Total general si el reporte define una columna a sumar
        $totalGeneral = null;
        if (!empty($def['totalKey'])) {
            $totalGeneral = 0;
            foreach ($filas as $fila) {
                $totalGeneral += (float) ($fila[$def['totalKey']] ?? 0);
            }
        }

        // Texto del rango de fechas para el encabezado
        $rangoTexto = '';
        if (!empty($def['usaFechas']) && (!empty($desde) || !empty($hasta))) {
            $d = !empty($desde) ? date('d/m/Y', strtotime($desde)) : 'Inicio';
            $h = !empty($hasta) ? date('d/m/Y', strtotime($hasta)) : 'Hoy';
            $rangoTexto = "Periodo: $d - $h";
        }

        $data = [
            'titulo'       => $def['titulo'],
            'fecha'        => date('d/m/Y'),
            'hora'         => date('H:i:s'),
            'columnas'     => $def['columnas'],
            'filas'        => $filas,
            'totalGeneral' => $totalGeneral,
            'totalKey'     => $def['totalKey'] ?? null,
            'rangoTexto'   => $rangoTexto,
        ];

        $this->renderPdf('reportes/pdf_generico', $data, 'reporte_' . $tipo . '.pdf');
    }

    /* ------------------------------------------------------------------ */
    /* Helper para generar y enviar cualquier PDF al navegador            */
    /* ------------------------------------------------------------------ */
    private function renderPdf(string $vista, array $data, string $nombreArchivo): void
    {
        $options = new Options();
        $options->set('isHtml5ParserEnabled', true);
        $options->set('isRemoteEnabled', true);

        $dompdf = new Dompdf($options);
        $dompdf->loadHtml(view($vista, $data));
        $dompdf->setPaper('A4', 'landscape');
        $dompdf->render();
        $dompdf->stream($nombreArchivo, ['Attachment' => false]);
    }


    public function pdfVentas()
    {
        if (session('rol') !== 'Administrador') {
            return redirect()->to('dashboard')->with('error', 'Acceso denegado');
        }

        $facturaModel = new FacturaModel();
        $facturas = $facturaModel->obtenerFacturas();

        $totalGeneral = 0;
        foreach ($facturas as $factura) {
            $totalGeneral += floatval($factura['Total']);
        }

          $data = [
            'titulo'       => 'Reporte Especifico de Ventas - Facturas',
            'fecha'        => date('d/m/Y'),
            'hora'         => date('H:i:s'),
            'facturas'     => $facturas,
            'totalGeneral' => $totalGeneral,
        ];

        $options = new Options();
        $options->set('isHtml5ParserEnabled', true);
        $options->set('isRemoteEnabled', true);

        $dompdf = new Dompdf($options);
        $dompdf->loadHtml(view('reportes/pdf_ventas', $data));
        $dompdf->setPaper('A4', 'portrait');
        $dompdf->render();
        $dompdf->stream('reporte_ventas.pdf', ['Attachment' => false]);
    }

    public function pdfProductos()
    {
        if (session('rol') !== 'Administrador') {
            return redirect()->to('dashboard')->with('error', 'Acceso denegado');
        }

        $menuModel = new MenuModel();
        $data = [
            'titulo'    => 'Reporte de Productos - Sistema de Gestion',
            'fecha'     => date('d/m/Y'),
            'hora'      => date('H:i:s'),
            'productos' => $menuModel->obtenerProductosConCategoria(),
        ];

        $options = new Options();
        $options->set('isHtml5ParserEnabled', true);
        $options->set('isRemoteEnabled', true);

        $dompdf = new Dompdf($options);
        $dompdf->loadHtml(view('reportes/pdf_productos', $data));
        $dompdf->setPaper('A4', 'portrait');
        $dompdf->render();
        $dompdf->stream('reporte_productos.pdf', ['Attachment' => false]);
    }

    public function pdfUsuarios()
    {
        if (session('rol') !== 'Administrador') {
            return redirect()->to('dashboard')->with('error', 'Acceso denegado');
        }

        $personaModel = new AdminPersonaModel();
        $data = [
            'titulo'   => 'Reporte de Usuarios - Sistema de Gestion',
            'fecha'    => date('d/m/Y'),
            'hora'     => date('H:i:s'),
            'usuarios' => $personaModel->obtenerUsuarios(),
        ];

        $options = new Options();
        $options->set('isHtml5ParserEnabled', true);
        $options->set('isRemoteEnabled', true);

        $dompdf = new Dompdf($options);
         $dompdf->loadHtml(view('reportes/pdf_usuarios', $data));
        $dompdf->setPaper('A4', 'portrait');
        $dompdf->render();
        $dompdf->stream('reporte_usuarios.pdf', ['Attachment' => false]);
    }
}