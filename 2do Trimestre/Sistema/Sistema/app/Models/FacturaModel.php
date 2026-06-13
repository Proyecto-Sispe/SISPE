<?php

namespace App\Models;

use CodeIgniter\Model;

class FacturaModel extends Model
{
    protected $table            = 'Factura';
    protected $primaryKey       = 'id_factura';
    protected $useAutoIncrement = true;
    protected $returnType       = 'array';
    protected $allowedFields    = ['id_pedido', 'Fecha_hora', 'Total'];

    // Mapea la información general cruzando tablas para el panel de control
    public function obtenerFacturas($buscar = '')
    {
        $builder = $this->select('
                Factura.id_factura, 
                Factura.id_pedido, 
                Factura.Fecha_hora, 
                Factura.Total, 
                Pedido.id_mesa, 
                Sesion_Mesa.nombre_cliente,
                fmp.pkfk_metodo_pago AS metodos_pago
            ')
            ->join('Pedido', 'Factura.id_pedido = Pedido.id_pedido')
            ->join('Sesion_Mesa', 'Pedido.id_sesion_qr = Sesion_Mesa.id_sesion', 'left')
            ->join('Factura_has_Metodo_pago fmp', 'Factura.id_factura = fmp.pkfk_n_factura', 'left');

        // Si el usuario escribe algo en el buscador del panel, filtra los resultados
        if (!empty($buscar)) {
            $builder->groupStart()
                    ->like('Sesion_Mesa.nombre_cliente', $buscar)
                    ->orLike('Factura.id_factura', $buscar)
                    ->orLike('Pedido.id_mesa', $buscar)
                    ->groupEnd();
        }

        return $builder->orderBy('Factura.Fecha_hora', 'DESC')->findAll();
    }
}