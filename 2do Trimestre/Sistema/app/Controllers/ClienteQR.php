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
            
            // Lo mandamos directo al Menú Digital para que arme su pedido
            return redirect()->to(base_url('menu_digital'));
            
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

        $id_pedido = $session->get('id_pedido');

        // Cabecera del pedido (estado, hora, tiempo estimado)
        $pedido = $db->table('Pedido')->where('id_pedido', $id_pedido)->get()->getRowArray();

        // Detalle del pedido cruzado con el menú real
        $items = $db->table('Detalle_Pedido dp')
                    ->select('dp.cantidad, dp.valor_venta, dp.observaciones, m.Productos, m.descripcion')
                    ->join('Menu m', 'm.id_menu = dp.id_menu')
                    ->where('dp.id_pedido', $id_pedido)
                    ->get()->getResultArray();

        // Totales
        $total = 0;
        $totalItems = 0;
        foreach ($items as $it) {
            $total      += $it['valor_venta'] * $it['cantidad'];
            $totalItems += $it['cantidad'];
        }

        $data['id_mesa']    = $session->get('id_mesa');
        $data['nombre']     = $session->get('nombre');
        $data['pedido']     = $pedido;
        $data['items']      = $items;
        $data['total']      = $total;
        $data['totalItems'] = $totalItems;

        return view('cliente/formulario_pedido', $data);
    }

    // 4. Añade un producto al CARRITO en sesión (todavía no toca la base de datos)
    public function agregarCarrito()
    {
        $session = session();
        $db = \Config\Database::connect();

        $id_producto = $this->request->getPost('id_menu');

        // Traemos el producto real del menú
        $producto = $db->table('Menu')->where('id_menu', $id_producto)->get()->getRowArray();
        if (!$producto) {
            return redirect()->to(base_url('menu_digital'));
        }

        // Carrito guardado en sesión, indexado por id_menu
        $carrito = $session->get('carrito') ?? [];

        if (isset($carrito[$id_producto])) {
            // Si ya existe, solo sumamos una unidad
            $carrito[$id_producto]['cantidad'] += 1;
        } else {
            $carrito[$id_producto] = [
                'id_menu'  => $id_producto,
                'nombre'   => $producto['Productos'],
                'precio'   => $producto['Precio'],
                'cantidad' => 1,
            ];
        }

        $session->set('carrito', $carrito);

        // Volvemos al menú para seguir eligiendo
        return redirect()->to(base_url('menu_digital'));
    }

    // 4.1 Elimina un producto del carrito
    public function eliminarCarrito($id_producto)
    {
        $session = session();
        $carrito = $session->get('carrito') ?? [];

        if (isset($carrito[$id_producto])) {
            unset($carrito[$id_producto]);
            $session->set('carrito', $carrito);
        }

        return redirect()->to(base_url('menu_digital'));
    }

    // 4.2 Confirma el pedido: pasa todo el carrito (con comentario) a la base de datos
    public function confirmarPedido()
    {
        $session = session();
        $db = \Config\Database::connect();

        $id_pedido = $session->get('id_pedido');
        $carrito   = $session->get('carrito') ?? [];
        $comentario = $this->request->getPost('comentario'); // Comentario general del cliente

        if (empty($carrito)) {
            return redirect()->to(base_url('menu_digital'));
        }

        // Insertamos cada item del carrito en Detalle_Pedido
        foreach ($carrito as $item) {
            $db->table('Detalle_Pedido')->insert([
                'id_pedido'     => $id_pedido,
                'id_menu'       => $item['id_menu'],
                'cantidad'      => $item['cantidad'],
                'valor_venta'   => $item['precio'],
                'observaciones' => $comentario,
            ]);
        }

        // Vaciamos el carrito una vez confirmado
        $session->remove('carrito');

        // Muestra la pantalla "Mi Pedido" con el estado y el detalle actualizado
        return redirect()->to(base_url('cliente/pedido'));
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
