<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="<?= base_url('Logo 2.png') ?>" type="image/png">
    <link rel="stylesheet" href="<?= base_url('Agregar Mesa.Css') ?>"> 
    <title>Editar Mesa N° <?= $mesa['id_Mesa'] ?></title>
</head>
<body>
<nav>
  <ul class="menu">
    <li class="logo"><img src="<?= base_url('Logo 2.png') ?>" alt="Logo"></li>
    <li><a href="<?= base_url('mesas') ?>">Volver a Mesas</a></li>
  </ul>
</nav>

<section class="formulario-mesa" style="max-width: 500px; margin: 40px auto; background: #fff; padding: 30px; border: 2px solid gold; border-radius: 8px;">
  <h2>Editar Mesa N° <?= $mesa['id_Mesa'] ?></h2>
  
  <form action="<?= base_url('mesas/actualizar') ?>" method="POST" class="grid-form">
    
    <input type="hidden" name="id_mesa" value="<?= $mesa['id_Mesa'] ?>">

    <div style="margin-bottom: 15px;">
      <label style="font-weight: bold; display: block;">Capacidad de Asientos:</label>
      <input type="number" name="capacidad" value="<?= $mesa['Capacidad'] ?>" style="width: 100%; padding: 10px;" required>
    </div>

    <div style="margin-bottom: 15px;">
      <label style="font-weight: bold; display: block;">Ubicación en el local:</label>
      <input type="text" name="ubicacion" value="<?= $mesa['Ubicacion'] ?>" style="width: 100%; padding: 10px;" required>
    </div>

    <div style="margin-bottom: 15px;">
      <label style="font-weight: bold; display: block;">Estado Operativo:</label>
      <select name="estado" style="width: 100%; padding: 10px;">
          <option value="0" <?= $mesa['Estado'] == 0 ? 'selected' : '' ?>>0 - Libre</option>
          <option value="1" <?= $mesa['Estado'] == 1 ? 'selected' : '' ?>>1 - Ocupada</option>
      </select>
    </div>

    <div style="text-align: center; margin-top: 20px;">
        <button type="submit" style="background-color: gold; color: #333; border: none; padding: 12px 25px; border-radius: 5px; font-weight: bold; cursor: pointer; width: 100%;">Actualizar Cambios</button>
    </div>
  </form>
</section>
</body>
</html>