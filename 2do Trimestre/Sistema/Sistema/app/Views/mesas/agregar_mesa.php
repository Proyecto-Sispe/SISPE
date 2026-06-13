<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="<?= base_url('css/Logo 2.png') ?>" type="image/png">
    <link rel="stylesheet" href="<?= base_url('css/Agregar Mesa.Css') ?>">
    <title>Agregar Mesa</title>
</head>
<body>
<nav>
  <ul class="menu">
    <li class="logo"><img src="<?= base_url('css/Logo 2.png') ?>" alt="Logo"></li>
    <li><a href="<?= base_url('inicio') ?>">Inicio</a></li>
    <li><a href="<?= base_url('personas') ?>">Personas</a></li>
    <li><a href="<?= base_url('mesas/gestion') ?>">Gestión de Mesas</a></li>
    <li><a href="<?= base_url('menu') ?>">Menú</a></li>
    <li><a href="<?= base_url('productos') ?>">Productos</a></li>
    <li><a href="<?= base_url('facturas') ?>">Facturas</a></li>
    <li><a href="<?= base_url('pedidos') ?>">Pedidos</a></li>
    <li class="right"><a href="<?= base_url('login') ?>">Login</a></li>
    <li><a href="<?= base_url('registro') ?>">Registro</a></li>
  </ul>
</nav>

<section class="formulario-mesa">
  <h2>Registrar Nueva Mesa</h2>
  <form action="<?= base_url('mesas/guardar') ?>" method="POST" class="grid-form">
    <div>
      <label>Número de Mesa</label>
      <input type="number" name="id_mesa" placeholder="Ingresar número de mesa" required>
    </div>
    <div>
      <label>Capacidad (Asientos)</label>
      <input type="number" name="capacidad" placeholder="Ingresar cantidad de personas" required>
    </div>
    <div style="grid-column: span 2;">
      <label>Ubicación en el local</label>
      <input type="text" name="ubicacion" placeholder="Ej: Primer Piso, Terraza, Zona VIP" required>
    </div>
    <div style="grid-column: span 2; text-align: center; margin-top: 20px;">
        <button type="submit" style="background-color: gold; color: #333; border: none; padding: 12px 25px; border-radius: 5px; font-weight: bold; cursor: pointer; font-size: 16px;">Guardar e Insertar Mesa</button>
    </div>
  </form>
</section>
</body>
</html>