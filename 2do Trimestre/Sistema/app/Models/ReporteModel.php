<?php

namespace App\Models;

use CodeIgniter\Model;

/**
 * Modelo central de reportes.
 * Cada metodo arma una consulta multitabla y devuelve un arreglo de filas
 * listo para enviarse a la vista PDF generica.
 * Los metodos aceptan un rango de fechas opcional ($desde, $hasta) en formato Y-m-d.
 */
class ReporteModel extends Model
{
    protected $table      = 'Factura';
    protected $returnType = 'array';

    /* ------------------------------------------------------------------ */
    /* Helper para aplicar el rango de fechas a cualquier consulta         */
    /* ------------------------------------------------------------------ */
    private function rangoFecha($builder, string $campo, $desde, $hasta)
    {
        if (!empty($desde)) {
            $builder->where("DATE($campo) >=", $desde);
        }
        if (!empty($hasta)) {
            $builder->where("DATE($campo) <=", $hasta);
        }
        return $builder;
    }

    /* ================================================================== */
    /* 1. VENTAS DETALLADAS (Factura + Pedido + Sesion + Metodo de pago)  */
    /* ================================================================== */
    public function ventasDetalladas($desde = null, $hasta = null)
    {
        $b = $this->db->table('Factura f')
            ->select('f.id_factura, f.id_pedido, p.id_mesa, p.estado AS estado_pedido,
                      sm.nombre_cliente, f.Fecha_hora, f.Total,
                      GROUP_CONCAT(DISTINCT mp.Tipo_pago SEPARATOR ", ") AS metodos_pago')
            ->join('Pedido p', 'f.id_pedido = p.id_pedido', 'left')
            ->join('Sesion_Mesa sm', 'p.id_sesion_qr = sm.id_sesion', 'left')
            ->join('Factura_has_Metodo_pago fmp', 'f.id_factura = fmp.pkfk_n_factura', 'left')
            ->join('Metodo_pago mp', 'fmp.pkfk_metodo_pago = mp.id_pago', 'left')
            ->groupBy('f.id_factura');

        $this->rangoFecha($b, 'f.Fecha_hora', $desde, $hasta);
        return $b->orderBy('f.Fecha_hora', 'DESC')->get()->getResultArray();
    }

    /* ================================================================== */
    /* 2. VENTAS POR ITEM (Detalle + Menu + Categoria + Pedido)           */
    /* ================================================================== */
    public function ventasPorItem($desde = null, $hasta = null)
    {
        $b = $this->db->table('Detalle_Pedido dp')
            ->select('dp.id_pedido, m.Productos, c.nom_categoria, dp.cantidad,
                      dp.valor_venta, (dp.cantidad * dp.valor_venta) AS subtotal, p.fecha_pedido')
            ->join('Menu m', 'dp.id_menu = m.id_menu', 'left')
            ->join('Categoria c', 'm.pkfk_id_categoria = c.id_categoria', 'left')
            ->join('Pedido p', 'dp.id_pedido = p.id_pedido', 'left');

        $this->rangoFecha($b, 'p.fecha_pedido', $desde, $hasta);
        return $b->orderBy('p.fecha_pedido', 'DESC')->get()->getResultArray();
    }

    /* ================================================================== */
    /* 3. PRODUCTOS MAS VENDIDOS (Detalle + Menu + Categoria)             */
    /* ================================================================== */
    public function productosVendidos($desde = null, $hasta = null)
    {
        $b = $this->db->table('Detalle_Pedido dp')
            ->select('m.Productos, c.nom_categoria, SUM(dp.cantidad) AS unidades,
                      SUM(dp.cantidad * dp.valor_venta) AS total')
            ->join('Menu m', 'dp.id_menu = m.id_menu', 'left')
            ->join('Categoria c', 'm.pkfk_id_categoria = c.id_categoria', 'left')
            ->join('Pedido p', 'dp.id_pedido = p.id_pedido', 'left')
            ->groupBy('dp.id_menu');

        $this->rangoFecha($b, 'p.fecha_pedido', $desde, $hasta);
        return $b->orderBy('unidades', 'DESC')->get()->getResultArray();
    }

    /* ================================================================== */
    /* 4. VENTAS POR CATEGORIA (Detalle + Menu + Categoria)               */
    /* ================================================================== */
    public function ventasPorCategoria($desde = null, $hasta = null)
    {
        $b = $this->db->table('Detalle_Pedido dp')
            ->select('c.nom_categoria, SUM(dp.cantidad) AS unidades,
                      SUM(dp.cantidad * dp.valor_venta) AS total')
            ->join('Menu m', 'dp.id_menu = m.id_menu', 'left')
            ->join('Categoria c', 'm.pkfk_id_categoria = c.id_categoria', 'left')
            ->join('Pedido p', 'dp.id_pedido = p.id_pedido', 'left')
            ->groupBy('c.id_categoria');

        $this->rangoFecha($b, 'p.fecha_pedido', $desde, $hasta);
        return $b->orderBy('total', 'DESC')->get()->getResultArray();
    }

    /* ================================================================== */
    /* 5. VENTAS POR METODO DE PAGO (Factura_has_Metodo_pago + Metodo)    */
    /* ================================================================== */
    public function ventasPorMetodoPago($desde = null, $hasta = null)
    {
        $b = $this->db->table('Factura_has_Metodo_pago fmp')
            ->select('mp.Tipo_pago, COUNT(DISTINCT fmp.pkfk_n_factura) AS transacciones,
                      SUM(fmp.monto) AS total')
            ->join('Metodo_pago mp', 'fmp.pkfk_metodo_pago = mp.id_pago', 'left')
            ->join('Factura f', 'fmp.pkfk_n_factura = f.id_factura', 'left')
            ->groupBy('fmp.pkfk_metodo_pago');

        $this->rangoFecha($b, 'f.Fecha_hora', $desde, $hasta);
        return $b->orderBy('total', 'DESC')->get()->getResultArray();
    }

    /* ================================================================== */
    /* 6. PEDIDOS POR ESTADO (Pedido)                                     */
    /* ================================================================== */
    public function pedidosPorEstado($desde = null, $hasta = null)
    {
        $b = $this->db->table('Pedido')
            ->select('estado, COUNT(*) AS cantidad')
            ->groupBy('estado');

        $this->rangoFecha($b, 'fecha_pedido', $desde, $hasta);
        return $b->orderBy('cantidad', 'DESC')->get()->getResultArray();
    }

    /* ================================================================== */
    /* 7. PEDIDOS POR MESA (Pedido + Mesa + Sesion_Mesa)                  */
    /* ================================================================== */
    public function pedidosPorMesa($desde = null, $hasta = null)
    {
        $b = $this->db->table('Pedido p')
            ->select('p.id_pedido, p.id_mesa, me.Ubicacion, sm.nombre_cliente,
                      p.estado, p.prioridad, p.fecha_pedido')
            ->join('Mesa me', 'p.id_mesa = me.id_Mesa', 'left')
            ->join('Sesion_Mesa sm', 'p.id_sesion_qr = sm.id_sesion', 'left');

        $this->rangoFecha($b, 'p.fecha_pedido', $desde, $hasta);
        return $b->orderBy('p.fecha_pedido', 'DESC')->get()->getResultArray();
    }

    /* ================================================================== */
    /* 8. OCUPACION DE MESAS (Mesa + Pedido)                              */
    /* ================================================================== */
    public function ocupacionMesas($desde = null, $hasta = null)
    {
        $b = $this->db->table('Mesa me')
            ->select('me.id_Mesa, me.Capacidad, me.Ubicacion, me.Estado,
                      COUNT(p.id_pedido) AS total_pedidos')
            ->join('Pedido p', 'me.id_Mesa = p.id_mesa', 'left')
            ->groupBy('me.id_Mesa');

        return $b->orderBy('total_pedidos', 'DESC')->get()->getResultArray();
    }

    /* ================================================================== */
    /* 9. SESIONES DE CLIENTES (Sesion_Mesa + Mesa)                       */
    /* ================================================================== */
    public function sesionesClientes($desde = null, $hasta = null)
    {
        $b = $this->db->table('Sesion_Mesa sm')
            ->select('sm.id_sesion, sm.nombre_cliente, sm.cedula_cliente,
                      sm.id_mesa, me.Ubicacion, sm.fecha_inicio, sm.fecha_fin, sm.activa')
            ->join('Mesa me', 'sm.id_mesa = me.id_Mesa', 'left');

        $this->rangoFecha($b, 'sm.fecha_inicio', $desde, $hasta);
        return $b->orderBy('sm.fecha_inicio', 'DESC')->get()->getResultArray();
    }

    /* ================================================================== */
    /* 10. USUARIOS POR ROL (Persona + Tipo_doc + Persona_has_Rol + Rol)  */
    /* ================================================================== */
    public function usuariosPorRol($desde = null, $hasta = null)
    {
        $b = $this->db->table('Persona p')
            ->select('p.id_usuario, td.tipo_doc,
                      CONCAT_WS(" ", p.Nom1_usu, p.Nom2_usu, p.Ape1_usu, p.Ape2_usu) AS nombre,
                      p.Correo_usu, p.Telefono, r.Nom_rol, p.estado')
            ->join('Tipo_doc td', 'p.pkfk_Tipo_doc = td.id_doc', 'left')
            ->join('Persona_has_Rol phr', 'p.id_usuario = phr.pkfk_id_usuario AND p.pkfk_Tipo_doc = phr.pkfk_Tipo_doc', 'left')
            ->join('Rol r', 'phr.pkfk_idRol = r.idRol', 'left')
            ->where('p.estado', 1);

        return $b->orderBy('r.Nom_rol', 'ASC')->get()->getResultArray();
    }

    /* ================================================================== */
    /* 11. MENU POR CATEGORIA (Menu + Categoria)                          */
    /* ================================================================== */
    public function menuPorCategoria($desde = null, $hasta = null)
    {
        return $this->db->table('Menu m')
            ->select('m.id_menu, m.Productos, c.nom_categoria, m.Precio, m.descripcion')
            ->join('Categoria c', 'm.pkfk_id_categoria = c.id_categoria', 'left')
            ->orderBy('c.nom_categoria', 'ASC')
            ->get()->getResultArray();
    }

    /* ================================================================== */
    /* 12. DETALLE COMPLETO DE PEDIDOS (Pedido + Detalle + Menu + Mesa)   */
    /* ================================================================== */
    public function detallePedidosCompleto($desde = null, $hasta = null)
    {
        $b = $this->db->table('Pedido p')
            ->select('p.id_pedido, p.id_mesa, me.Ubicacion, m.Productos,
                      dp.cantidad, dp.valor_venta, (dp.cantidad * dp.valor_venta) AS subtotal,
                      p.estado, p.fecha_pedido')
            ->join('Detalle_Pedido dp', 'p.id_pedido = dp.id_pedido', 'left')
            ->join('Menu m', 'dp.id_menu = m.id_menu', 'left')
            ->join('Mesa me', 'p.id_mesa = me.id_Mesa', 'left');

        $this->rangoFecha($b, 'p.fecha_pedido', $desde, $hasta);
        return $b->orderBy('p.id_pedido', 'DESC')->get()->getResultArray();
    }

    /* ================================================================== */
    /* 13. RESUMEN GENERAL (KPIs de todas las tablas)                     */
    /* ================================================================== */
    public function resumenGeneral($desde = null, $hasta = null)
    {
        $db = $this->db;

        $totalFacturas = $db->table('Factura')->countAllResults();
        $totalVentas   = (float) ($db->table('Factura')->selectSum('Total')->get()->getRow()->Total ?? 0);
        $totalPedidos  = $db->table('Pedido')->countAllResults();
        $totalProductos = $db->table('Menu')->countAllResults();
        $totalUsuarios = $db->table('Persona')->where('estado', 1)->countAllResults();
        $totalMesas    = $db->table('Mesa')->countAllResults();
        $mesasOcupadas = $db->table('Mesa')->where('Estado', 1)->countAllResults();
        $totalSesiones = $db->table('Sesion_Mesa')->countAllResults();
        $unidadesVendidas = (int) ($db->table('Detalle_Pedido')->selectSum('cantidad')->get()->getRow()->cantidad ?? 0);
        $ticketPromedio = $totalFacturas > 0 ? $totalVentas / $totalFacturas : 0;

        return [
            ['indicador' => 'Ingresos totales facturados', 'valor' => $totalVentas, 'money' => true],
            ['indicador' => 'Ticket promedio por factura', 'valor' => $ticketPromedio, 'money' => true],
            ['indicador' => 'Total de facturas emitidas', 'valor' => $totalFacturas, 'money' => false],
            ['indicador' => 'Total de pedidos registrados', 'valor' => $totalPedidos, 'money' => false],
            ['indicador' => 'Unidades de producto vendidas', 'valor' => $unidadesVendidas, 'money' => false],
            ['indicador' => 'Productos activos en el menu', 'valor' => $totalProductos, 'money' => false],
            ['indicador' => 'Usuarios activos del sistema', 'valor' => $totalUsuarios, 'money' => false],
            ['indicador' => 'Mesas registradas', 'valor' => $totalMesas, 'money' => false],
            ['indicador' => 'Mesas ocupadas actualmente', 'valor' => $mesasOcupadas, 'money' => false],
            ['indicador' => 'Sesiones de cliente (QR) creadas', 'valor' => $totalSesiones, 'money' => false],
        ];
    }
}