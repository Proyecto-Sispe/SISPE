<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="<?php echo base_url('img/Logo 2.png'); ?>" type="image/png">
    <link rel="stylesheet" href="<?php echo base_url('css/Persona.css'); ?>">
    <title>Panel de Personas</title>
</head>
<body>
<nav>
  <ul class="menu">
    <li class="logo"><img src="<?php echo base_url('css/Logo 2.png'); ?>" alt="Logo"></li>
    <li><a href="<?= base_url('dashboard') ?>">Inicio</a></li>
    <li><a href="<?= base_url('personas') ?>">Personas</a></li>
    <li><a href="<?= base_url('mesas') ?>">Gestión de Mesas</a></li>
    <li><a href="<?= base_url('pedidos') ?>">Panel de Pedidos</a></li> 
    <li><a href="<?= base_url('gestion-menu') ?>">Menú (Admin)</a></li>
    <li><a href="<?= base_url('menu_digital') ?>" target="_blank">Menú Digital</a></li>
    <li><a href="<?= base_url('productos') ?>">Productos</a></li>
    <li><a href="<?= base_url('facturas') ?>">Facturas</a></li>
    <li class="right"><a href="<?php echo base_url('logout'); ?>">Cerrar Sesión</a></li>
  </ul>
</nav>

<section class="hero">
    <div>
        <h1>Gestión de Usuarios</h1>
        <p>Administra las credenciales, perfiles y roles de las personas vinculadas al sistema de forma centralizada.</p>
    </div>
    <a href="<?php echo base_url('personas/crear'); ?>" class="btn">Agregar Persona</a>
</section>

<section class="panel">
    
    <?php if(session()->getFlashdata('success')): ?>
        <p style="color: #2ec4b6; font-weight: bold; padding: 10px; border: 1px solid gold; border-radius: 5px;"><?php echo session()->getFlashdata('success'); ?></p>
    <?php endif; ?>

    <form method="GET" action="<?php echo base_url('personas'); ?>" class="filtros">
        <h3>Filtrar Búsqueda</h3>
        <div class="fila-filtros">
            <select name="doc">
                <option value="">Todos los Documentos</option>
                <option value="1" <?php echo ($filtro_doc == '1') ? 'selected' : ''; ?>>Cédula de Ciudadanía</option>
                <option value="2" <?php echo ($filtro_doc == '2') ? 'selected' : ''; ?>>Tarjeta de Identidad</option>
                <option value="3" <?php echo ($filtro_doc == '3') ? 'selected' : ''; ?>>Cédula de Extranjería</option>
            </select>

            <select name="rol">
                <option value="">Todos los Roles</option>
                <option value="1" <?php echo ($filtro_rol == '1') ? 'selected' : ''; ?>>Administrador</option>
                <option value="2" <?php echo ($filtro_rol == '2') ? 'selected' : ''; ?>>Cocinero</option>
                <option value="3" <?php echo ($filtro_rol == '3') ? 'selected' : ''; ?>>Mesero</option>
                <option value="4" <?php echo ($filtro_rol == '4') ? 'selected' : ''; ?>>Cliente</option>
            </select>

            <input type="text" name="buscar" placeholder="Buscar por ID o Nombre..." value="<?php echo esc($filtro_text); ?>">
            
            <button type="submit" class="btn-buscar">Buscar</button>
        </div>
    </form>

    <div class="tabla">
        <h3>Registros Encontrados</h3>
        <table>
            <thead>
                <tr>
                    <th>Identificación</th>
                    <th>Tipo Doc</th>
                    <th>Nombres</th>
                    <th>Apellidos</th>
                    <th>Teléfono</th>
                    <th>Correo</th>
                    <th>Rol</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                <?php if(!empty($usuarios)): ?>
                    <?php foreach($usuarios as $user): ?>
                        <tr>
                            <td><?php echo $user['id_usuario']; ?></td>
                            <td><?php echo $user['nombre_documento']; ?></td>
                            <td><?php echo $user['Nom1_usu'] . ' ' . $user['Nom2_usu']; ?></td>
                            <td><?php echo $user['Ape1_usu'] . ' ' . $user['Ape2_usu']; ?></td>
                            <td><?php echo $user['Telefono']; ?></td>
                            <td><?php echo $user['Correo_usu']; ?></td>
                            <td>
                                <span class="rol admin"><?php echo $user['Nom_rol']; ?></span>
                            </td>
                            <td>
                                <a href="<?php echo base_url('personas/editar/'.$user['id_usuario'].'/'.$user['pkfk_Tipo_doc']); ?>">
                                    <button class="edit">✏️ Editar</button>
                                </a>
                                <a href="<?php echo base_url('personas/eliminar/'.$user['id_usuario'].'/'.$user['pkfk_Tipo_doc']); ?>" onclick="return confirm('¿Seguro deseas eliminar a este usuario?');">
                                    <button class="delete">🗑️ Eliminar</button>
                                </a>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                <?php else: ?>
                    <tr>
                        <td colspan="8" style="text-align: center; padding: 20px;">No se encontraron personas con los criterios ingresados.</td>
                    </tr>
                <?php endif; ?>
            </tbody>
        </table>
    </div>
</section>
</body>
</html>