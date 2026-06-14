<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="<?php echo base_url('img/Logo 2.png'); ?>" type="image/png">
    <link rel="stylesheet" href="<?php echo base_url('css/Login.Css'); ?>">
    <title>Restablecer Contraseña</title>
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
    <h1>Restablecer Contraseña</h1>

    <form method="POST" action="<?php echo base_url('reset-password'); ?>">

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

        <!-- Si el usuario llego por el enlace del correo, el token viaja oculto -->
        <input type="hidden" name="token" value="<?php echo esc($token ?? '', 'attr'); ?>">

        <?php if (empty($token)): ?>
            <p style="text-align:center; margin-bottom:15px;">
                Ingresa el correo y el código de 6 dígitos que recibiste, junto a tu nueva contraseña.
            </p>
            <div class="grid-inputs">
                <label for="email">Correo Electrónico:</label>
                <input type="email" id="email" name="email" required>

                <label for="codigo">Código de Verificación:</label>
                <input type="text" id="codigo" name="codigo" maxlength="6" placeholder="123456" required>

                <label for="password">Nueva Contraseña:</label>
                <input type="password" id="password" name="password" required>

                <label for="password_confirm">Confirmar Contraseña:</label>
                <input type="password" id="password_confirm" name="password_confirm" required>
            </div>
        <?php else: ?>
            <p style="text-align:center; margin-bottom:15px;">
                Ingresa tu nueva contraseña.
            </p>
            <div class="grid-inputs">
                <label for="password">Nueva Contraseña:</label>
                <input type="password" id="password" name="password" required>

                <label for="password_confirm">Confirmar Contraseña:</label>
                <input type="password" id="password_confirm" name="password_confirm" required>
            </div>
        <?php endif; ?>

        <div class="botones">
            <button type="submit" class="btn-login">Cambiar Contraseña</button>
            <p>¿No recibiste el código? <a href="<?php echo base_url('olvide-password'); ?>">Solicítalo de nuevo</a></p>
        </div>
    </form>
</main>

</body>
</html>