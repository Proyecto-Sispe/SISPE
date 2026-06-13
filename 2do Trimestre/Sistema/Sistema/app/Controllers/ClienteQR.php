<?php

namespace App\Controllers;

use App\Models\MesaModel;
use CodeIgniter\Controller;

class ClienteQR extends BaseController
{
    // 1. Se ejecuta automáticamente al escanear el QR: http://localhost/.../cliente/escanear/1
    public function escanear($id_mesa)
    {
        $db = \Config\Database::connect();
        
        // Consultamos el estado real de la mesa en tu tabla
        $mesa = $db->table('Mesa')->where('id_Mesa', $id_mesa)->get()->getRowArray();
        
        if (!$mesa) {
            return "La mesa escaneada no existe en el sistema.";
        }
        
        // Si la mesa está ocupada (Estado = 1), bloqueamos el acceso inmediatamente
        if ($mesa['Estado'] == 1) {
            return "<h1>Mesa Ocupada</h1><p>Esta mesa se encuentra ocupada en este momento. No puedes escanearla.</p>";
        }
        
        // Si está libre, le pasamos el número de mesa a la vista de registro temporal
        $data['id_mesa'] = $id_mesa;
        return view('cliente/registro_qr', $data);
    }

    // 2. Recibe el Nombre y Cédula del formulario especial del QR
    public function registrarAcceso()
    {
        $session = session();
        $db = \Config\Database::connect();
        
        $id_mesa = $this->request->getPost('id_mesa');
        $nombre  = $this->request->getPost('nombre_cliente');
        $cedula  = $this->request->getPost('cedula_cliente');
        
        try {
            // Ejecutamos tu Primer Procedimiento Almacenado de MySQL
            $query = $db->query("CALL RegistrarClienteYCrearPedido(?, ?, ?, @p_id_pedido_nuevo)", [
                $id_mesa, $nombre, $cedula
            ]);
            
            // Recogemos el ID del pedido que generó el procedimiento almacenado
            $res = $db->query("SELECT @p_id_pedido_nuevo AS id_pedido")->getRowArray();
            $id_pedido = $res['id_pedido'];
            
            // ASIGNACIÓN AUTOMÁTICA DEL ROL CLIENTE (ID 4) EN LA SESIÓN DE CODEIGNITER
            $session->set([
                'id_mesa'      => $id_mesa,
                'id_pedido'    => $id_pedido,
                'nombre'       => $nombre,
                'cedula'       => $cedula,
                'id_rol'       => 4, // Rol Cliente Automático
                'logged_in'    => true
            ]);
            
            // Lo mandamos directo al formulario de pedidos
            return redirect()->to(base_url('cliente/pedido'));
            
        } catch (\Exception $e) {
            return "Error al abrir la mesa: " . $e->getMessage();
        }
    }

    // 3. Muestra tu archivo Formulario Menu.Html adaptado
    public function pantallaPedido()
    {
        $session = session();
        if (!$session->get('logged_in') || $session->get('id_rol') != 4) {
            return redirect()->to(base_url('mesas'));
        }

        $db = \Config\Database::connect();
        
        // Traemos las categorías y los productos reales de tu menú para pintarlos
        $data['categorias'] = $db->table('Categoria')->get()->getResultArray();
        $data['productos']  = $db->table('Menu')->get()->getResultArray();
        $data['id_mesa']    = $session->get('id_mesa');
        $data['nombre']     = $session->get('nombre');

        return view('cliente/formulario_pedido', $data);
    }

    // 4. Guarda las categorías, productos y observaciones elegidas por el cliente
    public function guardarPedido()
    {
        $session = session();
        $db = \Config\Database::connect();
        
        $id_pedido   = $session->get('id_pedido');
        $id_producto = $this->request->getPost('id_menu'); // Producto del menú seleccionado
        $cantidad    = $this->request->getPost('cantidad');
        $observacion = $this->request->getPost('observacion'); // Ejemplo: "La quiero con papas y gaseosa..."
        
        // Traemos el precio real del producto desde tu tabla Menu
        $producto = $db->table('Menu')->where('id_menu', $id_producto)->get()->getRowArray();
        
        // Insertamos en tu tabla Detalle_Pedido real
        $db->table('Detalle_Pedido')->insert([
            'id_pedido'     => $id_pedido,
            'id_menu'       => $id_producto,
            'cantidad'      => $cantidad,
            'valor_venta'   => $producto['Precio'],
            'observaciones' => $observacion
        ]);
        
        // Redirecciona a la pantalla de éxito con el estado del cocinero
        return redirect()->to(base_url('cliente/estado'));
    }

    // 5. Pantalla final de Estado de Pedido (El reporte del cocinero)
    public function verEstado()
    {
        $session = session();
        $db = \Config\Database::connect();
        
        $id_pedido = $session->get('id_pedido');
        
        // Consultamos el estado actual del pedido en la base de datos
        $pedido = $db->table('Pedido')->where('id_pedido', $id_pedido)->get()->getRowArray();
        
        $data['estado'] = $pedido['estado']; // 'pendiente', 'en_preparacion', 'en_camino', 'entregado'
        return view('cliente/estado_pedido', $data);
    }
}