<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="<?php echo base_url('img/Logo 2.png'); ?>" type="image/png">
    <link rel="stylesheet" href="<?php echo base_url('css/Login.Css'); ?>">
    <title>Recuperar Contraseña</title>
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
    <h1>Recuperar Contraseña</h1>

    <form method="POST" action="<?php echo base_url('olvide-password'); ?>">

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
            Ingresa tu correo electrónico y te enviaremos un código para restablecer tu contraseña.
        </p>

        <div class="grid-inputs">
            <label for="email">Correo Electrónico:</label>
            <input type="email" id="email" name="email" required>
        </div>

        <div class="botones">
            <button type="submit" class="btn-login">Enviar Código</button>
            <p>¿Ya recuerdas tu contraseña? <a href="<?php echo base_url('/'); ?>">Inicia sesión</a></p>
            <p>¿Ya tienes un código? <a href="<?php echo base_url('reset-password'); ?>">Ingrésalo aquí</a></p>
        </div>
    </form>
</main>

</body>
</html>
