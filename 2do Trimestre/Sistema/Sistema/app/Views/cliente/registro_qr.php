<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Acceso Mesa N° <?= $id_mesa ?></title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #333; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .box { background: white; color: #333; padding: 30px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); text-align: center; width: 300px; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
        button { background: gold; color: #333; border: none; padding: 12px; width: 100%; font-weight: bold; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
<div class="box">
    <h2>Mesa N° <?= $id_mesa ?></h2>
    <p>Ingresa tus datos para iniciar tu orden</p>
    <form action="<?= base_url('cliente/registrar_acceso') ?>" method="POST">
        <input type="hidden" name="id_mesa" value="<?= $id_mesa ?>">
        <input type="text" name="nombre_cliente" placeholder="Tu Nombre Completo" required>
        <input type="number" name="cedula_cliente" placeholder="Número de Cédula" required>
        <button type="submit">Ingresar al Menú</button>
    </form>
</div>
</body>
</html>