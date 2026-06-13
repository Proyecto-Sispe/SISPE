<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Menú Digital</title>
    <style>
        body { margin: 0; background-color: #FA7F72; font-family: Arial, sans-serif; }
        nav { width: 100%; background-color: gray; }
        .menu { display: flex; align-items: center; list-style: none; margin: 0; padding: 0 20px; height: 60px; }
        .logo img { height: 45px; }
        .logo { margin-right: 30px; }
        .menu li a { font-weight: bold; padding: 10px 15px; color: white; text-decoration: none; }
        
        h1 { text-align: center; color: white; margin-top: 30px; font-size: 32px; text-transform: uppercase; }
        .subtitulo { text-align: center; color: #fff0ee; margin-bottom: 40px; }
        
        .contenedor-principal { max-width: 1100px; margin: 0 auto; padding: 0 20px 50px 20px; }
        .bloque-seccion { margin-bottom: 50px; }
        .nombre-seccion { color: white; font-size: 24px; border-bottom: 3px solid white; padding-bottom: 8px; margin-bottom: 25px; text-transform: uppercase; }
        
        .grid-tarjetas { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 30px; }
        
        /* TU TARJETA CLONADA EXACTA */
        .card {
            background-color: white; border-radius: 12px; padding: 25px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1); display: flex; flex-direction: column;
            justify-content: space-between; min-height: 240px;
        }
        .card h3 { margin: 0; color: #222; font-size: 22px; }
        .linea { width: 100%; height: 2px; background-color: #FA7F72; margin: 10px 0 15px 0; }
        .card p { color: #555; font-size: 14px; line-height: 1.5; margin: 0 0 20px 0; }
        .precio { font-size: 18px; font-weight: bold; color: #333; margin-bottom: 12px; }
        
        .btn-next {
            background-color: #FA7F72; color: white; border: none; padding: 12px;
            border-radius: 8px; font-weight: bold; text-align: center; text-decoration: none;
            font-size: 14px; text-transform: uppercase; display: block;
        }
    </style>
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

<h1>NUESTRO MENÚ SECCIONES</h1>
<p class="subtitulo">Elige tus platos favoritos organizados por categorías</p>

<div class="contenedor-principal">
    <?php foreach($menuCategorizado as $seccion => $platos): ?>
        <div class="bloque-seccion">
            <h2 class="nombre-seccion"><?= esc($seccion) ?></h2>
            <div class="grid-tarjetas">
                <?php foreach($platos as $p): ?>
                    <div class="card">
                        <div>
                            <h3><?= esc($p['Productos']) ?></h3>
                            <div class="linea"></div>
                            <p><?= esc($p['descripcion'] ?? 'Sin descripción disponible.') ?></p>
                        </div>
                        <div>
                            <div class="precio">$<?= number_format($p['Precio'], 0, ',', '.') ?></div>
                            <a href="#" class="btn-next">PEDIR</a>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>
    <?php endforeach; ?>
</div>

</body>
</html>