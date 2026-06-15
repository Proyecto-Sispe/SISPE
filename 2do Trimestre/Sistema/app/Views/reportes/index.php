<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="<?php echo base_url('css/Logo 2.png'); ?>" type="image/png">
    <link rel="stylesheet" href="<?php echo base_url('css/inicio.Css'); ?>">
    <style>
        .container-reportes {
            max-width: 1000px;
            margin: 40px auto;
            padding: 20px;
        }

        .header-reportes {
            background: #97a0c94f;
            color: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
            text-align: center;
        }

        .header-reportes h1 {
            margin: 0;
            font-size: 2.5em;
        }

        .header-reportes p {
            margin: 10px 0 0 0;
            font-size: 1.1em;
            opacity: 0.9;
        }

        .reportes-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .report-card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            padding: 25px;
            text-align: center;
            transition: transform 0.3s, box-shadow 0.3s;
        }

        .report-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
        }

        .report-card .icon {
            font-size: 3em;
            margin-bottom: 15px;
        }

        .report-card h3 {
            color: #333;
            margin: 15px 0;
            font-size: 1.4em;
        }

        .report-card p {
            color: #666;
            margin-bottom: 20px;
            font-size: 0.95em;
        }

        .btn-reporte {
            display: inline-block;
            padding: 12px 30px;
            background: #eab566c4;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            transition: background 0.3s;
            border: none;
            cursor: pointer;
            font-size: 1em;
        }

        .btn-reporte:hover {
            background: #764ba2;
        }

        .btn-reporte.secondary {
            background: #48bb78;
        }

        .btn-reporte.secondary:hover {
            background: #38a169;
        }

        .btn-volver {
            display: inline-block;
            margin-bottom: 20px;
            padding: 10px 20px;
            background: #e2e8f0;
            color: #2d3748;
            text-decoration: none;
            border-radius: 5px;
            transition: background 0.3s;
        }

        .btn-volver:hover {
            background: #cbd5e0;
        }
    </style>
</head>
<body>
<nav>
  <ul class="menu">
    <li class="logo">
      <img src="<?php echo base_url('css/Logo 2.png'); ?>" alt="Logo">
    </li>
    
    <li><a href="<?php echo base_url('dashboard'); ?>">Inicio</a></li>

    <?php if (session('rol') === 'Administrador'): ?>
    <li><a href="<?= base_url('personas') ?>">Personas</a></li>
    <li><a href="<?= base_url('mesas') ?>">Mesas</a></li>
    <li><a href="<?= base_url('mesas/agregar') ?>">Agregar Mesa</a></li>
    <li><a href="<?= base_url('menu') ?>">Menú</a></li>
    <li><a href="<?= base_url('productos') ?>">Productos</a></li>
    <li><a href="<?= base_url('facturas') ?>">Facturas</a></li>
    <li><a href="<?= base_url('pedidos') ?>">Pedidos</a></li>
    <li><a href="<?= base_url('reportes') ?>">Reportes</a></li>


    <?php elseif (session('rol') === 'Mesero'): ?>
      <li><a href="<?php echo base_url('mesas'); ?>">Mesas</a></li>
      <li><a href="<?php echo base_url('gestion-mesas'); ?>">Gestion de Mesas</a></li>
      <li><a href="<?php echo base_url('menu'); ?>">Menú</a></li>
      <li><a href="<?php echo base_url('productos'); ?>">Productos</a></li>
      <li><a href="<?php echo base_url('pedidos'); ?>">Pedidos</a></li>

    <?php elseif (session('rol') === 'Cliente'): ?>
      <li><a href="<?php echo base_url('mesas'); ?>">Mesas</a></li>
      <li><a href="<?php echo base_url('menu'); ?>">Menú</a></li>
    <?php endif; ?>

    <li class="right"><a href="<?php echo base_url('logout'); ?>">Cerrar Sesión</a></li>
  </ul>
</nav>

<div class="container-reportes">
    <!--<a href="?php echo base_url('dashboard')" class="btn-volver">← Volver al Inicio</a>-->

    <div class="header-reportes">
        <h1> Centro de Reportes</h1>
        <p>Descarga reportes en PDF de tu sistema</p>
    </div>

    <div class="reportes-grid">
        <div class="report-card">
            <div class="icon">📦</div>
            <h3>Reporte de Productos</h3>
            <p>Descarga un reporte completo de todos los productos disponibles en el menú con sus categorías, precios y descripciones.</p>
            <a href="<?php echo base_url('reportes/productos'); ?>" class="btn-reporte" target="_blank">
                Descargar PDF
            </a>
        </div>

        <div class="report-card">
            <div class="icon">👥</div>
            <h3>Reporte de Usuarios</h3>
            <p>Genera un reporte PDF con todos los usuarios activos, su documento, nombre, correo y rol.</p>
            <a href="<?php echo base_url('reportes/usuarios'); ?>" class="btn-reporte secondary" target="_blank">
                Descargar PDF
            </a>
        </div>

        <div class="report-card">
            <div class="icon">💰</div>
            <h3>Reporte Específico de Ventas</h3>
            <p>Visualiza el reporte de ventas con los detalles de transacciones y montos totales generados.</p>
            <a href="<?php echo base_url('reportes/pdf'); ?>" class="btn-reporte secondary" target="_blank">
                    Descargar PDF
            </a>
    </div>
</div>

<footer class="footer">
  <div class="footer-contenido">
    <div class="footer-izq">
      <h3>SISPE</h3>
      <p>Sistema de Gestión para Restaurantes</p>
    </div>
    <div class="footer-der">
      <p>© 2026 SISPE. Todos los derechos reservados.</p>
    </div>
  </div>
</footer>

</body>
</html>
