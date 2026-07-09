<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Menú Digital</title>
    <style>
        body { margin: 0; background-color:rgb(116, 111, 111); font-family: Arial, sans-serif; }
        nav { width: 100%; background-color: gray; }
        .menu { display: flex; align-items: center; list-style: none; margin: 0; padding: 0 20px; height: 60px; }
        .logo img { height: 45px; }
        .logo { margin-right: 30px; }
        .menu li a { font-weight: bold; padding: 10px 15px; color: white; text-decoration: none; }
        
        h1 { text-align: center; color: white; margin-top: 30px; font-size: 32px; text-transform: uppercase; }
        .subtitulo { text-align: center; color: #fff0ee; margin-bottom: 40px; }
        
          /* Layout de dos columnas: menú a la izquierda, carrito a la derecha */
        .layout { max-width: 1300px; margin: 0 auto; padding: 0 20px 50px 20px; display: flex; align-items: flex-start; gap: 30px; }
        .contenedor-principal { flex: 1; min-width: 0; }
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
            font-size: 14px; text-transform: uppercase; display: block; width: 100%;
            cursor: pointer;
        }
        .btn-next:hover { 
            background-color: #e96b5e; 
        }

        .form-pedir { 
            margin: 0; 
        }

         /* PANEL DEL CARRITO (columna lateral pegajosa, no tapa el contenido) */
        .carrito {
             flex: 0 0 320px; width: 320px; position: sticky; top: 20px;
            max-height: calc(100vh - 40px); overflow-y: auto;
            background-color: white; border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15); padding: 20px;
        }
        @media (max-width: 900px) {
            .layout { flex-direction: column; }
            .carrito { position: static; width: 100%; flex-basis: auto; max-height: none; }
        }
        .carrito h2 { margin: 0 0 5px 0; color: #222; font-size: 20px; }
        .carrito .mesa { color: #888; font-size: 13px; margin: 0 0 15px 0; }
        .carrito-vacio { color: #888; font-size: 14px; text-align: center; padding: 20px 0; }
        .carrito-item { display: flex; justify-content: space-between; align-items: flex-start; padding: 10px 0; border-bottom: 1px solid #eee; }
        .carrito-item .info { font-size: 14px; color: #333; }
        .carrito-item .info small { color: #888; display: block; }
        .carrito-item .precio-item { font-weight: bold; color: #333; font-size: 14px; white-space: nowrap; }
        .quitar { color: #FA7F72; font-size: 12px; text-decoration: none; }
        .carrito-total { display: flex; justify-content: space-between; font-weight: bold; color: #222; margin: 15px 0; font-size: 16px; }
        .carrito label { display: block; font-size: 13px; color: #555; margin-bottom: 6px; font-weight: bold; }
        .carrito textarea { width: 100%; box-sizing: border-box; border: 1px solid #ddd; border-radius: 8px; padding: 10px; font-family: inherit; font-size: 13px; resize: vertical; min-height: 60px; }
        .btn-hacer-pedido {
            width: 100%; background-color: #2ecc71; color: white; border: none; padding: 14px;
            border-radius: 8px; font-weight: bold; font-size: 15px; text-transform: uppercase;
            cursor: pointer; margin-top: 12px;
        }
        .btn-hacer-pedido:hover { background-color: #27ae60; }
        .btn-hacer-pedido:disabled { background-color: #bbb; cursor: not-allowed; }
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

<div class="layout">
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
                             <form action="<?= base_url('cliente/agregar_carrito') ?>" method="POST" class="form-pedir">
                                <input type="hidden" name="id_menu" value="<?= esc($p['id_menu']) ?>">
                                <button type="submit" class="btn-next">PEDIR</button>
                            </form>
                        </div>
                    </div>
                 <?php endforeach; ?>
            </div>
        </div>
    <?php endforeach; ?>
</div>
<?php
    $carrito = $carrito ?? [];
    $totalCarrito = 0;
    $totalItems = 0;
    foreach ($carrito as $item) {
        $totalCarrito += $item['precio'] * $item['cantidad'];
        $totalItems   += $item['cantidad'];
    }
?>
<aside class="carrito">
    <h2>Tu Pedido</h2>
    <p class="mesa">Mesa <?= esc(session('id_mesa')) ?> &middot; <?= (int) $totalItems ?> item(s)</p>

    <?php if (empty($carrito)): ?>
        <p class="carrito-vacio">Aún no has agregado productos.<br>Presiona <strong>PEDIR</strong> en un plato.</p>
    <?php else: ?>
        <?php foreach ($carrito as $item): ?>
            <div class="carrito-item">
                <div class="info">
                    <?= esc($item['cantidad']) ?>x <?= esc($item['nombre']) ?>
                    <small>
                        $<?= number_format($item['precio'], 0, ',', '.') ?> c/u
                        &middot;
                        <a class="quitar" href="<?= base_url('cliente/eliminar_carrito/' . $item['id_menu']) ?>">Quitar</a>
                    </small>
                </div>
                <div class="precio-item">$<?= number_format($item['precio'] * $item['cantidad'], 0, ',', '.') ?></div>
            </div>
        <?php endforeach; ?>

        <div class="carrito-total">
            <span>Total</span>
            <span>$<?= number_format($totalCarrito, 0, ',', '.') ?></span>
        </div>

        <form action="<?= base_url('cliente/confirmar_pedido') ?>" method="POST">
            <label for="comentario">Comentario (opcional)</label>
            <textarea id="comentario" name="comentario" placeholder="Ej: sin cebolla, término medio, con gaseosa..."></textarea>
            <button type="submit" class="btn-hacer-pedido">Hacer Pedido</button>
        </form>
    <?php endif; ?>
</aside>
</div>
</body>
</html>