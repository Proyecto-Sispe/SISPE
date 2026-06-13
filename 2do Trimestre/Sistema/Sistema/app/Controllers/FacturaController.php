<?php

namespace App\Controllers;

use App\Models\FacturaModel;
use CodeIgniter\Database\Config;

class FacturaController extends BaseController
{
    // Muestra el historial completo de facturas (panel_facturas.php)
    public function index()
    {
        if (!session('logueado')) return redirect()->to('/');

        $facturaModel = new FacturaModel();
        $buscar = trim($this->request->getGet('buscar') ?? '');
        
        // Trae las facturas cruzadas con el cliente, la mesa y el método de pago de la intermedia
        $facturas = $facturaModel->obtenerFacturas($buscar);

        return view('facturas/panel_facturas', ['facturas' => $facturas, 'buscar' => $buscar]);
    }

    // Muestra la visualización de la tirilla para imprimir (ver_factura.php)
    public function ver($id_factura)
    {
        if (!session('logueado')) return redirect()->to('/');

        $db = Config::connect();

        // Datos principales de la factura cruzados con la mesa, el cliente del QR y el método de pago
        $builder = $db->table('Factura f');
        $builder->select('f.id_factura, f.id_pedido, f.Fecha_hora, f.Total, p.id_mesa, sm.nombre_cliente, sm.cedula_cliente, fmp.pkfk_metodo_pago AS metodos_pago');
        $builder->join('Pedido p', 'f.id_pedido = p.id_pedido');
        $builder->join('Sesion_Mesa sm', 'p.id_sesion_qr = sm.id_sesion', 'left');
        $builder->join('Factura_has_Metodo_pago fmp', 'f.id_factura = fmp.pkfk_n_factura', 'left');
        $builder->where('f.id_factura', $id_factura);
        $data['factura'] = $builder->get()->getRowArray();

        if (!$data['factura']) {
            return redirect()->to('/facturas')->with('error', 'La factura no existe.');
        }

        // Trae los productos del menú consumidos en ese pedido específico
        $detBuilder = $db->table('Detalle_Pedido dp');
        $detBuilder->select('dp.cantidad, m.Productos, dp.valor_venta, (dp.cantidad * dp.valor_venta) AS subtotal');
        $detBuilder->join('Menu m', 'dp.id_menu = m.id_menu');
        $detBuilder->where('dp.id_pedido', $data['factura']['id_pedido']);
        $data['items'] = $detBuilder->get()->getResultArray();

        return view('facturas/ver_factura', $data);
    }

    // ARREGLADO: Recibe por POST el ID desde el formulario nativo para evitar el 404
    public function eliminar()
    {
        if (!session('logueado')) return redirect()->to('/');

        $id = $this->request->getPost('id_factura');

        if (empty($id)) {
            return redirect()->to('/facturas')->with('error', 'No se especificó una factura válida.');
        }

        $db = Config::connect();
        
        // Por integridad referencial en MySQL, borramos primero la relación intermedia y luego el maestro
        $db->query("DELETE FROM Factura_has_Metodo_pago WHERE pkfk_n_factura = ?", [$id]);
        $db->query("DELETE FROM Factura WHERE id_factura = ?", [$id]);

        return redirect()->to('/facturas')->with('mensaje', 'Factura eliminada de caja con éxito.');
    }
}

