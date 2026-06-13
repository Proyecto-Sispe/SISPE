<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="<?php echo base_url('css/Logo 2.png'); ?>" type="image/png">
    <link rel="stylesheet" href="<?php echo base_url('css/Dashboard.Css'); ?>">
    <title>Inicio SISPE</title>
</head>
<body>
<nav>
  <ul class="menu">
    <li class="logo">
      <img src="<?php echo base_url('css/Logo 2.png'); ?>" alt="Logo">
    </li>

    <?php if (session('rol') === 'Administrador'): ?>
      <li><a href="<?= base_url('dashboard') ?>">Inicio</a></li>
      <li><a href="<?= base_url('personas') ?>">Personas</a></li>
      <li><a href="<?= base_url('mesas') ?>">Gestión de Mesas</a></li>
      <li><a href="<?= base_url('pedidos') ?>">Panel de Pedidos</a></li> 

      <li><a href="<?= base_url('gestion-menu') ?>">Menú (Admin)</a></li>
      <li><a href="<?= base_url('menu_digital') ?>" target="_blank">Menú Digital</a></li>

      <li><a href="<?= base_url('productos') ?>">Productos</a></li>
      <li><a href="<?= base_url('facturas') ?>">Facturas</a></li>

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

<section class="hero">
  <div class="hero-contenido">
    <h1>Sistema de Gestión para Restaurantes</h1>
    <p>
      Bienvenido, <strong><?php echo session('nombre'); ?></strong>. Has ingresado con el rol de: <strong><?php echo session('rol'); ?></strong>.
    </p>
    <div class="botones">
      <a href="#" class="btn btn-principal">Panel de Control</a>
      <a href="#" class="btn btn-secundario">Ver mi Perfil</a>
    </div>
  </div>
  <div class="hero-icono">
    <img src="<?php echo base_url('css/Logo.png'); ?>" alt="Icono">
  </div>
</section>

<section class="modulos">
  <h2>Módulos del Sistema</h2>
  <div class="contenedor-modulos">
    
    <?php if (session('rol') === 'Administrador'): ?>
    <div class="card">
      <h3>Gestión de Personas</h3>
      <p>Administra clientes, meseros, cocineros y administradores.</p>
      <a href="<?php echo base_url('personas'); ?>" class="btn-card">Ver más</a>
    </div>
    
    <?php endif; ?>

    <div class="card">
      <h3>Control de Mesas</h3>
      <p>Gestiona disponibilidad, capacidad y ubicación.</p>
      <a href="<?php echo base_url('mesas'); ?>" class="btn-card">Ver más</a>
    </div>

    <div class="card">
      <h3>Menú Digital</h3>
      <p>Administra productos, categorías y precios.</p>
      <a href="<?php echo base_url('menu'); ?>" class="btn-card">Ver más</a>
    </div>

    <?php if (session('rol') === 'Administrador' || session('rol') === 'Mesero'): ?>
    <div class="card">
      <h3>Productos</h3>
      <p>Gestión y modificación de productos.</p>
      <a href="<?php echo base_url('productos'); ?>" class="btn-card">Ver más</a>
    </div>
    <div class="card">
      <h3>Pedidos</h3>
      <p>Controla pedidos en tiempo real.</p>
      <a href="<?php echo base_url('pedidos'); ?>" class="btn-card">Ver más</a>
    </div>
    <?php endif; ?>

    <?php if (session('rol') === 'Administrador'): ?>
    <div class="card">
      <h3>Facturación</h3>
      <p>Genera facturas y gestiona pagos.</p>
      <a href="<?php echo base_url('facturas'); ?>" class="btn-card">Ver más</a>
    </div>
    <?php endif; ?>

    <div class="card">
      <h3>Reportes</h3>
      <p>Genera reportes en PDF de productos, ventas y más.</p>
      <a href="<?php echo base_url('reportes'); ?>" class="btn-card">Ver más</a>
    </div>

  </div>
</section>

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



