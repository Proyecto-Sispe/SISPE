<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="<?= base_url('css/Logo 2.png') ?>" type="image/png">
    <link rel="stylesheet" href="<?= base_url('css/PanelPedidos.Css') ?>">
    <title>Panel de Cocina - Pedidos</title>
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
    <h1>Monitoreo de Pedidos en Cocina</h1>
    <p>Controla las comandas entrantes de los códigos QR en tiempo real</p>
</section>

<section class="panel-pedidos-container">
    
    <div class="grid-pedidos">
        
        <?php if(!empty($pedidos)): ?>
            <?php foreach($pedidos as $ped): ?>
                
                <div class="tarjeta-pedido">
                    <div class="pedido-header">
                        <h2>Mesa N° <?= $ped['id_mesa'] ?></h2>
                        <span class="hora"><?= date('h:i A', strtotime($ped['fecha_pedido'])) ?></span>
                    </div>

                    <p class="texto-cliente"><strong>Cliente:</strong> <?= $ped['nombre_cliente'] ?? 'Anonimo (QR)' ?></p>
                    
                    <p class="titulo-productos">Productos solicitados:</p>
                    <ul class="lista-productos">
                        <?php foreach($ped['items'] as $item): ?>
                            <li class="item-producto">
                                <strong>(x<?= $item['cantidad'] ?>)</strong> <?= $item['Productos'] ?>
                                <?php if(!empty($item['adiciones'])): ?>
                                    <br><small class="nota-adicional">↳ Nota: <?= $item['adiciones'] ?></small>
                                <?php endif; ?>
                            </li>
                        <?php endforeach; ?>
                    </ul>

                    <p class="estado-contenedor"><strong>Estado Actual:</strong> 
                        <?php if($ped['estado'] == 'pendiente'): ?>
                            <span class="badge-estado estado-espera">⏳ En Espera</span>
                        <?php elseif($ped['estado'] == 'en_preparacion'): ?>
                            <span class="badge-estado estado-preparacion">🍳 En Preparación</span>
                        <?php elseif($ped['estado'] == 'en_camino'): ?>
                            <span class="badge-estado estado-camino">🛵 En Camino</span>
                        <?php endif; ?>
                    </p>

                    <div class="acciones-cocina">
                        <?php if($ped['estado'] == 'pendiente'): ?>
                            <a href="<?= base_url('cocina/cambiarestado/'.$ped['id_pedido'].'/en_preparacion') ?>" class="btn-accion btn-preparar">
                                👨‍🍳 Empezar Preparación
                            </a>
                        <?php elseif($ped['estado'] == 'en_preparacion'): ?>
                            <a href="<?= base_url('cocina/cambiarestado/'.$ped['id_pedido'].'/en_camino') ?>" class="btn-accion class btn-camino">
                                🚀 Marcar "En Camino"
                            </a>
                        <?php elseif($ped['estado'] == 'en_camino'): ?>
                            <a href="<?= base_url('cocina/cambiarestado/'.$ped['id_pedido'].'/entregado') ?>" 
                               onclick="return confirm('¿Completar el pedido? Esto liberará la mesa automáticamente en el salón.');"
                               class="btn-accion btn-completar">
                                🍽 Pedido Completado (Liberar Mesa)
                            </a>
                        <?php endif; ?>
                    </div>
                </div>

            <?php endforeach; ?>
        <?php else: ?>
            <div class="sin-pedidos">
                <h3>📭 No hay pedidos pendientes</h3>
                <p>La cocina está al día. Cuando un cliente escanee un QR y pida, aparecerá aquí instantáneamente.</p>
            </div>
        <?php endif; ?>

    </div>
</section>
</body>
</html>