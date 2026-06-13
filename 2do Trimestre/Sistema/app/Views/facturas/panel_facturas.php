<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="<?= base_url('css/Logo 2.png') ?>" type="image/png">
    <link rel="stylesheet" href="<?= base_url('css/Factura.Css') ?>">
    <title>Historial de Facturas</title>
</head>
<body>
<nav>
  <ul class="menu">
    <li class="logo"><img src="<?= base_url('css/Logo 2.png') ?>" alt="Logo"></li>
    <li><a href="<?= base_url('dashboard') ?>">Inicio</a></li>
    <li><a href="<?= base_url('personas') ?>">Personas</a></li>
    <li><a href="<?= base_url('mesas') ?>">Gestión de Mesas</a></li>
    <li><a href="<?= base_url('pedidos') ?>">Panel de Pedidos</a></li> 
    <li><a href="<?= base_url('gestion-menu') ?>">Menú (Admin)</a></li>
    <li><a href="<?= base_url('menu_digital') ?>" target="_blank">Menú Digital</a></li>
    <li><a href="<?= base_url('productos') ?>">Productos</a></li>
    <li><a href="<?= base_url('facturas') ?>">Facturas</a></li>
    <li class="right"><a href="<?php echo base_url('logout'); ?>">Cerrar Sesión</a></li>
  </ul>
</nav>

<section class="hero">
    <h1>Módulo de Facturación Caja</h1>
    <p>Consulta los ingresos recaudados y gestiona las tirillas de pago</p>
</section>

<section class="buscador-facturas">
    <p class="titulo-filtro">Filtrar Búsqueda</p>
    <form action="<?= base_url('facturas') ?>" method="get" class="formulario-busqueda">
        <input type="text" name="buscar" value="<?= esc($buscar ?? '') ?>" placeholder="Buscar por número, mesa o cliente..." class="input-buscar">
        <button type="submit" class="btn-buscar">Buscar</button>
        <?php if(!empty($buscar)): ?>
            <a href="<?= base_url('facturas') ?>" class="btn-limpiar">❌ Limpiar</a>
        <?php endif; ?>
    </form>
</section>

<section class="panel-facturas">
    <div class="contenedor-tabla-referencia">
        
        <div class="cabecera-registros">
            Registros Encontrados
        </div>

        <table class="tabla-facturas">
            <thead>
                <tr>
                    <th>N° Factura</th>
                    <th>Mesa</th>
                    <th>Cliente</th>
                    <th>Fecha y Hora</th>
                    <th>Método de Pago</th>
                    <th>Total Recaudado</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                <?php if(!empty($facturas)): ?>
                    <?php foreach($facturas as $fac): ?>
                        <tr>
                            <td style="font-weight: bold;"># <?= $fac['id_factura'] ?></td>
                            <td>Mesa N° <?= $fac['id_mesa'] ?></td>
                            <td><?= $fac['nombre_cliente'] ?? 'Personal Interno' ?></td>
                            <td><?= date('d/m/Y - h:i A', strtotime($fac['Fecha_hora'])) ?></td>
                            
                            <td>
                                <span class="badge-metodo">
                                    <?= $fac['metodos_pago'] ?? 'Efectivo' ?>
                                </span>
                            </td>

                            <td style="font-weight: bold; color: #51ff51;">$<?= number_format($fac['Total'], 0, ',', '.') ?></td>
                            <td>
                                <a href="<?= base_url('factura/ver/'.$fac['id_factura']) ?>" class="btn-accion-ver">
                                    Ver Tirilla / Imprimir
                                </a>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                <?php else: ?>
                    <tr>
                        <td colspan="7" class="sin-facturas">
                            <h3 style="margin: 0;">📭 No se encontraron facturas registradas</h3>
                        </td>
                    </tr>
                <?php endif; ?>
            </tbody>
        </table>
    </div>
</section>
</body>
</html>