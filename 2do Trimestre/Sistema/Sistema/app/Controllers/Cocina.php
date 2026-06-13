<?php

namespace App\Controllers;

use App\Models\PedidoModel; // Importas tu modelo

class Cocina extends BaseController
{
    // 1. Carga la pantalla con el listado de pedidos activos
    public function index()
    {
        $pedidoModel = new PedidoModel();

        // El modelo hace exactamente el mismo JOIN pero de forma más estructurada
        $data['pedidos'] = $pedidoModel->select('Pedido.id_pedido, Pedido.id_mesa, Pedido.estado, Pedido.fecha_pedido, Pedido.observaciones, Sesion_Mesa.nombre_cliente')
            ->join('Sesion_Mesa', 'Pedido.id_sesion_qr = Sesion_Mesa.id_sesion', 'left')
            ->whereIn('Pedido.estado', ['pendiente', 'en_preparacion', 'en_camino'])
            ->orderBy('Pedido.fecha_pedido', 'ASC')
            ->findAll();

        $db = \Config\Database::connect();
        foreach ($data['pedidos'] as &$pedido) {
            $pedido['items'] = $db->table('Detalle_Pedido dp')
                ->select('dp.cantidad, m.Productos, dp.observaciones AS adiciones')
                ->join('Menu m', 'dp.id_menu = m.id_menu')
                ->where('dp.id_pedido', $pedido['id_pedido'])
                ->get()->getResultArray();
        }

        return view('cocina/panel_pedidos', $data);
    }

    // =============================================================================
    // ¡ESTA ERA LA FUNCIÓN QUE TE FALTABA AQUÍ ADENTRO! (En minúsculas para el 404)
    // =============================================================================
    public function cambiarestado($id_pedido, $nuevo_estado)
    {
        $db = \Config\Database::connect();

        if ($nuevo_estado == 'entregado') {
            // Si el pedido se completó, llamamos a tu procedimiento almacenado seguro
            // Este procedimiento pone el pedido como entregado y LIBERA LA MESA automáticamente
            $db->query("CALL DespacharPedidoYLiberarMesa(?)", [$id_pedido]);
        } else {
            // Si es "en_preparacion" o "en_camino", actualizamos la columna en la tabla Pedido
            $db->table('Pedido')->where('id_pedido', $id_pedido)->update([
                'estado' => $nuevo_estado
            ]);
        }

        // Al terminar, recarga el panel de pedidos para ver el cambio reflejado
        return redirect()->to(base_url('pedidos'));
    }
}