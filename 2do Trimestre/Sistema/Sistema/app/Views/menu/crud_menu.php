<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestión de Menú</title>
    <style>
        body {
            margin: 0; 
            background-color: white;
            font-family: Arial, sans-serif;
        }

        nav {
            width: 100%;
            background-color: gray;
        }

        .menu {
            display: flex; 
            align-items: center;
            list-style: none; 
            margin: 0;
            padding: 0 20px;
            height: 60px;
        }

        .logo img {
            height: 45px;
        }

        .logo {
            margin-right: 30px;
        }

        .menu li {
            margin-right: 20px;
        }

        .right {
            margin-left: auto;
        }

        .menu li a {
            font-weight: bold;
            padding: 10px 15px;
            color: white;
            text-decoration: none;
            transition: 0.3s;
        }

        .menu li a:hover {
            color: gold;
        }

        h1 {
            text-align: center;
            color: gray;
            margin-top: 30px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Contenedor del formulario en dos columnas */
        .contenedor-formularios {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            max-width: 1100px;
            margin: 20px auto;
            padding: 0 20px;
        }

        form {
            background-color: gray;
            color: white;
            display: flex;
            flex-direction: column; 
            border-radius: 10px;
            border: 1px solid gold;
            padding: 25px;
            box-sizing: border-box;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }

        form h2 {
            color: gold;
            margin-top: 0;
            font-size: 20px;
            text-align: center;
            border-bottom: 1px dashed rgba(255,255,255,0.2);
            padding-bottom: 10px;
            margin-bottom: 15px;
        }

        .grid-inputs {
            display: grid;
            grid-template-columns: 1fr; 
            gap: 12px;
        }

        label {
            font-weight: bold;
            font-size: 14px;
        }

        input, select, textarea {
            width: 100%;
            background-color: white;
            color: gray;
            border-radius: 8px;
            padding: 10px;
            border: none;
            box-sizing: border-box;
            font-size: 14px;
        }

        input:focus, select:focus, textarea:focus {
            outline: 2px solid gold;
        }

        .botones {
            margin-top: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .botones button {
            background-color: gold;
            border: none;
            padding: 12px 20px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: bold;
            color: black;
            width: 100%;
            font-size: 14px;
            transition: 0.2s;
        }

        .botones button:hover {
            background-color: #e6c200;
        }

        /* Alertas de sesión */
        .alerta {
            max-width: 1100px;
            margin: 15px auto;
            padding: 12px;
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
        }
    </style>
</head>
<body>

<nav>
  <ul class="menu">
    <li class="logo"><img src="<?= base_url('css/Logo 2.png') ?>" alt="Logo"></li>
    <li><a href="<?= base_url('inicio') ?>">Inicio</a></li>
    <li><a href="<?= base_url('personas') ?>">Personas</a></li>
    <li><a href="<?= base_url('mesas') ?>">Gestión de Mesas</a></li>
    <li><a href="<?= base_url('pedidos') ?>">Panel de Pedidos</a></li> 
    <li><a href="<?= base_url('gestion-menu') ?>">Menú (Admin)</a></li>
    <li><a href="<?= base_url('menu_digital') ?>" target="_blank">Menú Digital</a></li>
    <li><a href="<?= base_url('productos') ?>">Productos</a></li>
    <li><a href="<?= base_url('facturas') ?>">Facturas</a></li>
    <li class="right"><a href="<?= base_url('login') ?>">Login</a></li>
    <li><a href="<?= base_url('registro') ?>">Registro</a></li>
  </ul>
</nav>

<h1>Panel de Administración del Menú</h1>

<?php if (session()->getFlashdata('mensaje')): ?>
    <div class="alerta">
        <?= session()->getFlashdata('mensaje') ?>
    </div>
<?php endif; ?>

<div class="contenedor-formularios">
    
    <div>
        <form action="<?= base_url('menu/guardarCategoria') ?>" method="POST">
            <h2>1. REGISTRAR CATEGORÍA</h2>
            <div class="grid-inputs">
                <div>
                    <label>Código / ID Categoría (Manual):</label>
                    <input type="text" name="id_categoria" required placeholder="Ej: 1, 2, CAT01...">
                </div>
                <div>
                    <label>Nombre de la Categoría:</label>
                    <input type="text" name="nom_categoria" required placeholder="Ej: Salchipapas, Bebidas, Gaseosas...">
                </div>
            </div>
            <div class="botones">
                <button type="submit">+ Guardar Categoría</button>
            </div>
        </form>
    </div>

    <div>
        <form action="<?= base_url('menu/guardar') ?>" method="POST">
            <h2>2. CREAR NUEVO PLATO</h2>
            <div class="grid-inputs">
                <div>
                    <label>Código / ID Producto (Manual):</label>
                    <input type="text" name="id_menu" required placeholder="Ej: 101, SAL01, GAS02...">
                </div>
                <div>
                    <label>Nombre del Producto:</label>
                    <input type="text" name="Productos" required placeholder="Ej: Coca-Cola 350ml">
                </div>
                <div>
                    <label>Seleccionar Categoría:</label>
                    <select name="pkfk_id_categoria" required>
                        <option value="">Seleccione una categoría...</option>
                        <?php if(!empty($categorias)): ?>
                            <?php foreach($categorias as $c): ?>
                                <option value="<?= $c['id_categoria'] ?>"><?= esc($c['nom_categoria']) ?></option>
                            <?php endforeach; ?>
                        <?php endif; ?>
                    </select>
                </div>
                <div>
                    <label>Descripción:</label>
                    <textarea name="descripcion" rows="1" placeholder="Breve detalle de los ingredientes..."></textarea>
                </div>
                <div>
                    <label>Precio de Venta ($):</label>
                    <input type="number" name="Precio" required placeholder="Ej: 5000">
                </div>
            </div>
            <div class="botones">
                <button type="submit">Guardar Producto</button>
            </div>
        </form>
    </div>

</div>

<hr style="max-width: 1100px; border: 1px dashed #ccc; margin: 40px auto;">

<div style="max-width: 1100px; margin: 0 auto; padding: 0 20px 60px 20px;">
    <h2 style="text-align: center; color: #333; margin-bottom: 20px; text-transform: uppercase; font-size: 20px;">Platos en el Sistema</h2>
    
    <table style="width: 100%; border-collapse: collapse; box-shadow: 0 4px 8px rgba(0,0,0,0.05); background-color: white; border-radius: 8px; overflow: hidden;">
        <thead>
            <tr style="background-color: #333; color: gold; text-align: left;">
                <th style="padding: 14px;">Código ID</th>
                <th style="padding: 14px;">Producto</th>
                <th style="padding: 14px;">Categoría Asignada</th>
                <th style="padding: 14px;">Precio</th>
                <th style="padding: 14px; text-align: center;">Acciones</th>
            </tr>
        </thead>
        <tbody>
            <?php if(!empty($productos)): ?>
                <?php foreach($productos as $p): ?>
                    <tr style="border-bottom: 1px solid #eee; background-color: #fff;">
                        <td style="padding: 14px; color: #666; font-family: monospace;"><?= esc($p['id_menu']) ?></td>
                        <td style="padding: 14px; font-weight: bold; color: #222;"><?= esc($p['Productos']) ?></td>
                        <td style="padding: 14px;"><span style="background: #eee; padding: 4px 10px; border-radius: 20px; font-size: 13px; color: #444;"><?= esc($p['nom_categoria']) ?></span></td>
                        <td style="padding: 14px; color: green; font-weight: bold;">$<?= number_format($p['Precio'], 0, ',', '.') ?></td>
                        <td style="padding: 14px; text-align: center;">
                            <a href="<?= base_url('menu/eliminar/'.$p['id_menu']) ?>" style="background-color: #ffcccc; color: red; padding: 6px 14px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: bold; transition: 0.2s;" onclick="return confirm('¿Estás seguro de eliminar este producto del menú?')">Eliminar</a>
                        </td>
                    </tr>
                <?php endforeach; ?>
            <?php else: ?>
                <tr>
                    <td colspan="5" style="text-align: center; padding: 30px; color: gray;">No hay productos registrados en el menú todavía.</td>
                </tr>
            <?php endif; ?>
        </tbody>
    </table>
</div>

</body>
</html>