<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="<?= base_url('css/Logo 2.png') ?>" type="image/png">
    <link rel="stylesheet" href="<?= base_url('css/Mesas 2.Css?v=1.1') ?>">
    <title>Gestión de Mesas</title>
</head>
<body>
<nav>
  <ul class="menu">
    <li class="logo"><img src="<?= base_url('css/Logo 2.png') ?>" alt="Logo"&gt;</li>
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
  <div class="hero-texto">
    <h1>Panel de Control de Mesas</h1>
    <p>Visualiza el estado de las mesas en tiempo real, edita sus datos o imprime sus códigos QR permanentes</p>
  </div>
  <div class="hero-boton">
    <a href="<?= base_url('mesas/agregar') ?>" class="btn">+ Agregar Nueva Mesa</a>
  </div>
</section>

<section class="panel">
  <h3>Estructura y Simulación de Salón</h3>
  
  <div class="grid-mesas-sistema">
    
    <?php if(!empty($mesas) && is_array($mesas)): ?>
        <?php foreach($mesas as $mesa): ?>
            
            <div class="card-mesa-item">
                <h2>Mesa N° <?= $mesa['id_Mesa'] ?></h2>
                <p><strong>Ubicación:</strong> <?= $mesa['Ubicacion'] ?></p>
                <p><strong>Capacidad:</strong> <?= $mesa['Capacidad'] ?> Asientos</p>
                
                <p><strong>Estado:</strong> 
                    <?php if($mesa['Estado'] == 0): ?>
                        <span class="estado-mesa estado-libre">Libre</span>
                    <?php else: ?>
                        <span class="estado-mesa estado-ocupada">Ocupada</span>
                    <?php endif; ?>
                </p>
                
                <div class="acciones-mesa">
                    <a href="<?= base_url('mesas/editar/'.$mesa['id_Mesa']) ?>" class="btn-editar">
                        ✏️ Editar Datos
                    </a>
                    
                    <a href="<?= base_url('mesas/eliminar/'.$mesa['id_Mesa']) ?>" 
                       onclick="return confirm('¿Seguro que deseas eliminar la Mesa N° <?= $mesa['id_Mesa'] ?>?\n\n¡Advertencia!: Esto borrará de forma permanente sus pedidos, facturas y sesiones de QR asociadas en el sistema.');"
                       class="btn-eliminar">
                        ❌ Eliminar Mesa
                    </a>
                    
                    <a href="https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=<?= urlencode(base_url('cliente/escanear/'.$mesa['id_Mesa'])) ?>" 
                       target="_blank" 
                       class="btn-qr">
                        🖨️ Ver / Imprimir QR
                    </a>
                </div>
            </div>

        <?php endforeach; ?>
    <?php else: ?>
        <div class="sin-mesas">
            <p style="font-size: 16px; font-weight: bold; margin: 0 0 10px 0;">No existen mesas registradas en la base de datos.</p>
            <p style="margin: 0;">Dale al botón de arriba para registrar e insertar la primera mesa del local.</p>
        </div>
    <?php endif; ?>

  </div>
</section>
</body>
</html>