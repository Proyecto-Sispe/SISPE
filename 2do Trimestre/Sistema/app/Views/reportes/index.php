<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="<?php echo base_url('css/Logo 2.png'); ?>" type="image/png">
    <link rel="stylesheet" href="<?php echo base_url('css/inicio.Css'); ?>">
    <style>
        .container-reportes {
            max-width: 1150px;
            margin: 40px auto;
            padding: 20px;
        }

        .header-reportes {
            background: #97a0c94f;
            color: #2d3748;
            padding: 28px;
            border-radius: 10px;
            margin-bottom: 28px;
            text-align: center;
        }

        .header-reportes h1 { margin: 0; font-size: 2.3em; }
        .header-reportes p { margin: 8px 0 0 0; font-size: 1.05em; opacity: 0.85; }

        /* ---- Barra de consultas multitabla ---- */
        .consulta-bar {
            background: #ffffff;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            padding: 26px;
            margin-bottom: 36px;
            border-top: 4px solid #eab566;
        }

        .consulta-bar h2 {
            margin: 0 0 6px 0;
            color: #374151;
            font-size: 1.4em;
        }

        .consulta-bar .sub {
            margin: 0 0 20px 0;
            color: #6b7280;
            font-size: 0.95em;
        }

        .consulta-form {
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            align-items: flex-end;
        }

        .form-group { display: flex; flex-direction: column; flex: 1 1 220px; }
        .form-group.fechas { flex: 0 1 180px; }

        .form-group label {
            font-size: 0.82em;
            font-weight: bold;
            color: #4b5563;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }

        .form-group select,
        .form-group input {
            padding: 11px 12px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 0.95em;
            background: #fff;
            color: #1f2937;
        }

        .form-group select:focus,
        .form-group input:focus {
            outline: none;
            border-color: #eab566;
            box-shadow: 0 0 0 3px rgba(234,181,102,0.25);
        }

        .btn-generar {
            flex: 0 0 auto;
            padding: 12px 32px;
            background: #111827;
            color: #fff;
            border: none;
            border-radius: 6px;
            font-weight: bold;
            font-size: 1em;
            cursor: pointer;
            transition: background 0.25s;
        }
        .btn-generar:hover { background: #374151; }

        .hint {
            margin-top: 14px;
            font-size: 0.82em;
            color: #9ca3af;
        }

        /* ---- Reportes generales (un boton -> PDF) ---- */
        .seccion-titulo {
            color: #374151;
            font-size: 1.3em;
            margin: 0 0 6px 0;
        }
        .seccion-sub { color: #6b7280; margin: 0 0 20px 0; font-size: 0.95em; }

        .reportes-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 18px;
            margin-bottom: 30px;
        }

        .report-card {
            background: #fff;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            padding: 22px;
            text-align: center;
            display: flex;
            flex-direction: column;
            transition: transform 0.25s, box-shadow 0.25s;
        }
        .report-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 6px 18px rgba(0,0,0,0.14);
        }
        .report-card .icon { font-size: 2.4em; margin-bottom: 10px; }
        .report-card .grupo {
            font-size: 0.7em;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            color: #b45309;
            font-weight: bold;
            margin-bottom: 6px;
        }
        .report-card h3 { color: #1f2937; margin: 4px 0 10px 0; font-size: 1.12em; }
        .report-card p { color: #6b7280; margin: 0 0 18px 0; font-size: 0.88em; flex-grow: 1; }

        .btn-reporte {
            display: inline-block;
            padding: 11px 22px;
            background: #eab566;
            color: #1f2937;
            text-decoration: none;
            border-radius: 6px;
            font-weight: bold;
            transition: background 0.25s;
            font-size: 0.92em;
        }
        .btn-reporte:hover { background: #d99b3f; }
    </style>
</head>
<body>
<nav>
  <ul class="menu">
    <li class="logo">
      <img src="<?php echo base_url('css/Logo 2.png'); ?>" alt="Logo">
    </li>

    <li><a href="<?php echo base_url('dashboard'); ?>">Inicio</a></li>

    <?php if (session('rol') === 'Administrador'): ?>
    <li><a href="<?= base_url('personas') ?>">Personas</a></li>
    <li><a href="<?= base_url('mesas') ?>">Mesas</a></li>
    <li><a href="<?= base_url('mesas/agregar') ?>">Agregar Mesa</a></li>
    <li><a href="<?= base_url('menu') ?>">Menú</a></li>
    <li><a href="<?= base_url('productos') ?>">Productos</a></li>
    <li><a href="<?= base_url('facturas') ?>">Facturas</a></li>
    <li><a href="<?= base_url('pedidos') ?>">Pedidos</a></li>
    <li><a href="<?= base_url('reportes') ?>">Reportes</a></li>
    <?php endif; ?>

    <li class="right"><a href="<?php echo base_url('logout'); ?>">Cerrar Sesión</a></li>
  </ul>
</nav>

<div class="container-reportes">

    <div class="header-reportes">
        <h1>Centro de Reportes</h1>
        <p>Genera consultas multitabla y descarga el PDF al instante</p>
    </div>

    <?php if (session()->getFlashdata('error')): ?>
        <div style="background:#fee2e2;color:#991b1b;padding:12px 16px;border-radius:6px;margin-bottom:20px;">
            <?= esc(session()->getFlashdata('error')) ?>
        </div>
    <?php endif; ?>

    <!-- ============ BARRA DE CONSULTAS MULTITABLA ============ -->
    <div class="consulta-bar">
        <h2>Consulta Personalizada</h2>
        <p class="sub">Elige el reporte que necesitas, aplica un rango de fechas opcional y descarga el PDF.</p>

        <form class="consulta-form" action="<?= base_url('reportes/generar') ?>" method="get" target="_blank">
            <div class="form-group">
                <label for="tipo">Tipo de reporte</label>
                <select name="tipo" id="tipo" required>
                    <option value="" disabled selected>Selecciona un reporte...</option>
                    <?php
                        // Agrupamos las opciones por su categoria para el desplegable
                        $grupos = [];
                        foreach ($reportes as $clave => $def) {
                            $grupos[$def['grupo']][$clave] = $def['titulo'];
                        }
                    ?>
                    <?php foreach ($grupos as $nombreGrupo => $opciones): ?>
                        <optgroup label="<?= esc($nombreGrupo) ?>">
                            <?php foreach ($opciones as $clave => $titulo): ?>
                                <option value="<?= esc($clave) ?>"><?= esc($titulo) ?></option>
                            <?php endforeach; ?>
                        </optgroup>
                    <?php endforeach; ?>
                </select>
            </div>

            <div class="form-group fechas">
                <label for="desde">Desde</label>
                <input type="date" name="desde" id="desde">
            </div>

            <div class="form-group fechas">
                <label for="hasta">Hasta</label>
                <input type="date" name="hasta" id="hasta">
            </div>

            <button type="submit" class="btn-generar">Consultar y Generar PDF</button>
        </form>

        <p class="hint">El rango de fechas solo se aplica a los reportes que registran fecha (ventas, pedidos, sesiones). El PDF se abre en una pestaña nueva.</p>
    </div>

    <!-- ============ REPORTES GENERALES (UN BOTON -> PDF) ============ -->
    <h2 class="seccion-titulo">Reportes Generales</h2>
    <p class="seccion-sub">Reportes ya predeterminados: un solo clic y obtienes el PDF completo.</p>

    <div class="reportes-grid">
        <?php foreach ($reportes as $clave => $def): ?>
            <div class="report-card">
                <div class="icon"><?= $def['icono'] ?? '&#128196;' ?></div>
                <div class="grupo"><?= esc($def['grupo']) ?></div>
                <h3><?= esc($def['titulo']) ?></h3>
                <p><?= esc($def['desc']) ?></p>
                <a class="btn-reporte" target="_blank"
                   href="<?= base_url('reportes/generar?tipo=' . $clave) ?>">
                    Descargar PDF
                </a>
            </div>
        <?php endforeach; ?>
    </div>

</div>

<footer class="footer">
  <div class="footer-contenido">
    <div class="footer-izq">
      <h3>SISPE</h3>
      <p>Sistema de Gestión para Restaurantes</p>
    </div>
    <div class="footer-der">
      <p>© 2026 SISPE. Todos los derechos reservados.</p>
    </div>
  </div>
</footer>

</body>
</html>
