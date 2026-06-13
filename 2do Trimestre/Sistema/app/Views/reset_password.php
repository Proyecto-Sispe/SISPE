<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="<?php echo base_url('img/Logo 2.png'); ?>" type="image/png">
    <link rel="stylesheet" href="<?php echo base_url('css/Login.Css'); ?>">
    <title>Nueva Contraseña</title>
</head>
<body>

<nav>
    <ul class="menu">
        <li class="logo">
            <img src="<?php echo base_url('css/Logo 2.png'); ?>" alt="Logo">
        </li>
        <li><a href="<?php echo base_url('/'); ?>">Inicio</a></li>
        <li class="right"><a href="<?php echo base_url('registro'); ?>">Registro</a></li>
    </ul>
</nav>

<main class="container">
    <h1>Nueva Contraseña</h1>

    <form method="POST" action="<?php echo base_url('reset-password'); ?>">

        <input type="hidden" name="token" value="<?php echo esc($token, 'attr'); ?>">

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

        <p style="text-align:center; margin-bottom:15px;">
            Escribe tu nueva contraseña.
        </p>

        <div class="grid-inputs">
            <label for="password">Nueva Contraseña:</label>
            <input type="password" id="password" name="password" required minlength="4">

            <label for="password_confirm">Confirmar Contraseña:</label>
            <input type="password" id="password_confirm" name="password_confirm" required minlength="4">
        </div>

        <div class="botones">
            <button type="submit" class="btn-login">Actualizar contraseña</button>
            <p><a href="<?php echo base_url('/'); ?>">Volver a iniciar sesión</a></p>
        </div>
    </form>
</main>

</body>
</html>
