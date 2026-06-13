<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="<?php echo base_url('css/Agregar Persona.css'); ?>">
    <link rel="icon" href="<?php echo base_url('img/Logo 2.png'); ?>" type="image/png">
    <title>Agregar Persona</title>
</head>
<body>
<nav>
  <ul class="menu">
    <li class="logo"><img src="<?php echo base_url('css/Logo 2.png'); ?>" alt="Logo"></li>
    <li><a href="<?php echo base_url('dashboard'); ?>">Inicio</a></li>
    <li><a href="<?php echo base_url('personas'); ?>">Personas</a></li>
    <li class="right"><a href="<?php echo base_url('logout'); ?>">Cerrar Sesión</a></li>
  </ul>
</nav>

<section class="formulario">
  <h2>Registrar Nueva Persona</h2>
  <form action="<?php echo base_url('personas/guardar'); ?>" method="POST">
    <div class="grid-form">
      <div>
        <label>Tipo de Documento</label>
        <select name="pkfk_Tipo_doc" required>
          <option value="1">Cédula de Ciudadanía</option>
          <option value="2">Tarjeta de Identidad</option>
          <option value="3">Cédula de Extranjería</option>
        </select>
      </div>
      <div>
        <label>Rol Asignado</label>
        <select name="id_rol" required>
          <option value="1">Administrador</option>
          <option value="2">Cocinero</option>
          <option value="3">Mesero</option>
          <option value="4">Cliente</option>
        </select>
      </div>
      <div>
        <label>Número de Identificación</label>
        <input type="text" name="id_usuario" maxlength="10" required>
      </div>
      <div>
        <label>Primer Nombre</label>
        <input type="text" name="Nom1_usu" maxlength="20" required>
      </div>
      <div>
        <label>Segundo Nombre</label>
        <input type="text" name="Nom2_usu" maxlength="20">
      </div>
      <div>
        <label>Primer Apellido</label>
        <input type="text" name="Ape1_usu" maxlength="20" required>
      </div>
      <div>
        <label>Segundo Apellido</label>
        <input type="text" name="Ape2_usu" maxlength="20">
      </div>
      <div>
        <label>Email</label>
        <input type="email" name="Correo_usu" maxlength="45" required>
      </div>
      <div>
        <label>Teléfono</label>
        <input type="number" name="Telefono" required>
      </div>
      <div>
        <label>Contraseña</label>
        <input type="password" name="Password" placeholder="********" required>
      </div>
    </div>
    <div class="acciones">
      <a href="<?php echo base_url('personas'); ?>" class="cancelar" style="text-decoration:none; display:inline-block; line-height:35px; text-align:center;">Cancelar</a>
      <button class="guardar" type="submit">Guardar</button>
    </div>
  </form>
</section>
</body>
</html>