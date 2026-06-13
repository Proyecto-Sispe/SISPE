<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="<?php echo base_url('css/Logo 2.png'); ?>" type="image/png">
    <link rel="stylesheet" href="<?php echo base_url('css/Registro.Css'); ?>">
    <title>Registro Usuario</title>
</head>
<body>
<nav>
    <ul class="menu">
        <li class="logo"><img src="<?php echo base_url('css/Logo 2.png'); ?>" alt="Logo"></li>
        <li><a href="<?php echo base_url('personas'); ?>">Personas</a></li>
        <li><a href="<?php echo base_url('/'); ?>">Inicio</a></li>
        <li class="right"><a href="<?php echo base_url('/'); ?>">Login</a></li>
    </ul>
</nav>
<section class="formulario">
    <h2>Registrar Nueva Persona</h2>
    
    <form action="<?php echo base_url('guardar'); ?>" method="POST">
        <div class="grid-form">
            <div>
                <label>Tipo Documento</label>
                <select id="doc" name="doc" required>
                    <option value="1">Cédula de ciudadanía</option>
                    <option value="2">Tarjeta de identidad</option>
                    <option value="3">Cédula de extranjería</option>
                </select>
            </div>
            
            <div>
                <label>Identificación</label>
                <input type="text" id="id" name="id" required>
            </div>
            <div>
                <label>Primer Nombre</label>
                <input type="text" id="nombre1" name="nombre1" required>
            </div>
            <div>
                <label>Segundo Nombre</label>
                <input type="text" id="nombre2" name="nombre2">
            </div>
            <div>
                <label>Primer Apellido</label>
                <input type="text" id="apellido1" name="apellido1" required>
            </div>
            <div>
                <label>Segundo Apellido</label>
                <input type="text" id="apellido2" name="apellido2">
            </div>
            <div>
                <label>Email</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div>
                <label>Teléfono</label>
                <input type="text" id="telefono" name="telefono" required>
            </div>
            <div>
                <label>Password</label>
                <input type="password" id="password" name="password" required>
            </div>
        </div>
        <div class="acciones">
            <button class="cancelar" type="reset">Cancelar</button>
            <button class="guardar" type="submit">Enviar</button>
        </div>
    </form>
</section>
</body>
</html>