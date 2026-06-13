<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="<?php echo base_url('img/Logo 2.png'); ?>" type="image/png">
    <link rel="stylesheet" href="<?php echo base_url('css/Login.Css'); ?>">
    <title>Inicio de Sesión</title>
</head>
<body>

<nav>
    <ul class="menu">
        <li class="logo">
            <img src="<?php echo base_url('css/Logo 2.png'); ?>" alt="Logo">
        </li>
        <li><a href="<?php echo base_url('/'); ?>">Inicio</a></li>
        <li><a href="#">Personas</a></li>
        <li><a href="#">Mesas</a></li>
        <li><a href="#">Menú</a></li>
        <li><a href="#">Facturas</a></li>
        <li><a href="#">Pedidos</a></li>
        <li class="right"><a href="<?php echo base_url('registro'); ?>">Registro</a></li>
    </ul>
</nav>

<main class="container">
    <h1>Inicio de Sesión</h1>

    <form method="POST" action="<?php echo base_url('login'); ?>">
        
        <?php if(session()->getFlashdata('error')): ?>
            <div style="background-color: #ff4d4d; color: white; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 15px; font-weight: bold; border: 1px solid gold;">
                <?php echo session()->getFlashdata('error'); ?>
            </div>
        <?php endif; ?>

        <?php if(session()->getFlashdata('mensaje')): ?>
            <div style="background-color: #2ec4b6; color: white; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 15px; font-weight: bold; border: 1px solid gold;">
                <?php echo session()->getFlashdata('mensaje'); ?>
            </div>
        <?php endif; ?>

        <div class="grid-inputs">
            <label for="email">Correo Electrónico:</label>
            <input type="email" id="email" name="email" required>

            <label for="password">Contraseña:</label>
            <input type="password" id="password" name="password" required>
        </div>

        <div class="botones">
            <button type="submit" class="btn-login">Iniciar Sesión</button>
            <p><a href="<?php echo base_url('olvide-password'); ?>">¿Olvidaste tu contraseña?</a></p>
            <p>¿No tienes cuenta? <a href="<?php echo base_url('registro'); ?>">Crea una aquí</a></p>
        </div>
    </form>
</main>

</body>
</html>