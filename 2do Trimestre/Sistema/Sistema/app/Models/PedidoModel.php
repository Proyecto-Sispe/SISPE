<?php

namespace App\Models;

use CodeIgniter\Model;

class PedidoModel extends Model
{
    protected $table            = 'Pedido';
    protected $primaryKey       = 'id_pedido';
    protected $useAutoIncrement = true;
    protected $returnType       = 'array';
    
    // Habilitamos todos los campos reales de tu tabla para que CodeIgniter los pueda leer y actualizar
    protected $allowedFields    = [
        'id_mesa', 
        'mesero_tipo_doc', 
        'mesero_id_usuario', 
        'cliente_tipo_doc', 
        'cliente_id_usuario', 
        'id_sesion_qr', 
        'fecha_pedido', 
        'estado', 
        'prioridad', 
        'cocinero_asignado', 
        'tiempo_estimado', 
        'observaciones'
    ];
}