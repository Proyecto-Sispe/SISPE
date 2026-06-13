<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Realizar Pedido - Mesa <?= $id_mesa ?></title>
    <link rel="stylesheet" href="<?= base_url('css/Formulario Menu.Css') ?>">
</head>
<body>

<main class="contenedor-pedido">
    <h2>Hola, <?= $nombre ?>. Armar pedido para Mesa <?= $id_mesa ?></h2>
    
    <form action="<?= base_url('cliente/guardar_pedido') ?>" method="POST" class="formulario-pedido">
        
        <div class="grupo-campo">
            <label for="id_menu">Select the main product:</label>
            <select name="id_menu" id="id_menu" required>
                <?php foreach($productos as $prod): ?>
                    <option value="<?= $prod['id_menu'] ?>"><?= $prod['Productos'] ?> - $<?= number_format($prod['Precio'], 0, ',', '.') ?></option>
                <?php endforeach; ?>
            </select>
        </div>

        <div class="grupo-campo">
            <label for="cantidad">Cantidad:</label>
            <input type="number" name="cantidad" id="cantidad" value="1" min="1" required>
        </div>

        <div class="grupo-campo">
            <label for="observacion">Observaciones y Adiciones:</label>
            <textarea name="observacion" id="observacion" placeholder="Ej: La quiero con papas, Gaseosa y extra salsa de queso..." required></textarea>
        </div>

        <button type="submit" class="btn-enviar-pedido">Confirmar y Enviar Pedido</button>
    </form>
</main>

</body>
</html>