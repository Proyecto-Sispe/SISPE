<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="<?php echo base_url('css/Agregar Persona.css'); ?>">
    <link rel="icon" href="<?php echo base_url('img/Logo 2.png'); ?>" type="image/png">
    <title>Modificar Persona</title>
</head>
<body>
<nav>
  <ul class="menu">
    <li class="logo"><img src="<?php echo base_url('img/Logo 2.png'); ?>" alt="Logo"></li>
    <li><a href="<?php echo base_url('dashboard'); ?>">Inicio</a></li>
    <li><a href="<?php echo base_url('personas'); ?>">Personas</a></li>
    <li class="right"><a href="<?php echo base_url('logout'); ?>">Cerrar Sesión</a></li>
  </ul>
</nav>

<section class="formulario">
  <h2>Modificar Datos de Persona</h2>
  <form action="<?php echo base_url('personas/actualizar'); ?>" method="POST">
    
    <input type="hidden" name="id_original" value="<?php echo $persona['id_usuario']; ?>">
    <input type="hidden" name="doc_original" value="<?php echo $persona['pkfk_Tipo_doc']; ?>">

    <div class="grid-form">
      <div>
        <label>Tipo de Documento (No modificable)</label>
        <select disabled style="background-color: #ddd;">
          <option value="1" <?php echo ($persona['pkfk_Tipo_doc'] == 1)?'selected':''; ?>>Cédula de Ciudadanía</option>
          <option value="2" <?php echo ($persona['pkfk_Tipo_doc'] == 2)?'selected':''; ?>>Tarjeta de Identidad</option>
          <option value="3" <?php echo ($persona['pkfk_Tipo_doc'] == 3)?'selected':''; ?>>Cédula de Extranjería</option>
        </select>
      </div>
      <div>
        <label>Rol del Usuario</label>
        <select name="id_rol" required>
          <option value="1" <?php echo ($persona['id_role'] ?? $persona['id_rol'] == 1)?'selected':''; ?>>Administrador</option>
          <option value="2" <?php echo ($persona['id_role'] ?? $persona['id_rol'] == 2)?'selected':''; ?>>Cocinero</option>
          <option value="3" <?php echo ($persona['id_role'] ?? $persona['id_rol'] == 3)?'selected':''; ?>>Mesero</option>
          <option value="4" <?php echo ($persona['id_role'] ?? $persona['id_rol'] == 4)?'selected':''; ?>>Cliente</option>
        </select>
      </div>
      <div>
        <label>Número de Identificación (No modificable)</label>
        <input type="text" value="<?php echo $persona['id_usuario']; ?>" disabled style="background-color: #ddd;">
      </div>
      <div>
        <label>Primer Nombre</label>
        <input type="text" name="Nom1_usu" value="<?php echo $persona['Nom1_usu']; ?>" maxlength="20" required>
      </div>
      <div>
        <label>Segundo Nombre</label>
        <input type="text" name="Nom2_usu" value="<?php echo $persona['Nom2_usu']; ?>" maxlength="20">
      </div>
      <div>
        <label>Primer Apellido</label>
        <input type="text" name="Ape1_usu" value="<?php echo $persona['Ape1_usu']; ?>" maxlength="20" required>
      </div>
      <div>
        <label>Segundo Apellido</label>
        <input type="text" name="Ape2_usu" value="<?php echo $persona['Ape2_usu']; ?>" maxlength="20">
      </div>
      <div>
        <label>Email</label>
        <input type="email" name="Correo_usu" value="<?php echo $persona['Correo_usu']; ?>" maxlength="45" required>
      </div>
      <div>
        <label>Teléfono</label>
        <input type="number" name="Telefono" value="<?php echo $persona['Telefono']; ?>" required>
      </div>
      <div>
        <label>Nueva Contraseña (Dejar vacío para no cambiar)</label>
        <input type="password" name="Password" placeholder="********">
      </div>
    </div>
    <div class="acciones">
      <a href="<?php echo base_url('personas'); ?>" class="cancelar" style="text-decoration:none; display:inline-block; line-height:35px; text-align:center;">Cancelar</a>
      <button class="guardar" type="submit">Actualizar Cambios</button>
    </div>
  </form>
</section>
</body>
</html>