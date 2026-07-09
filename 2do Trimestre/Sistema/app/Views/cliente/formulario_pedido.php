<?php
    // ---- Datos de estado y tiempo ----
    $estado = $pedido['estado'] ?? 'pendiente';

    $badge = 'Pendiente';
    if ($estado == 'en_preparacion') $badge = 'En Preparación';
    elseif ($estado == 'en_camino')  $badge = 'En Camino';
    elseif ($estado == 'entregado')  $badge = 'Listo';

    // Nivel de progreso: 1=Confirmado, 2=En Cocina, 3=En Preparación, 4=Listo
    $nivel = 1;
    if ($estado == 'pendiente')            $nivel = 2;
    elseif ($estado == 'en_preparacion')   $nivel = 3;
    elseif ($estado == 'en_camino')        $nivel = 3;
    elseif ($estado == 'entregado')        $nivel = 4;

    // "Realizado hace X minutos"
    $hace = 'hace un momento';
    if (!empty($pedido['fecha_pedido'])) {
        $min = max(0, floor((time() - strtotime($pedido['fecha_pedido'])) / 60));
        $hace = 'Realizado hace ' . $min . ' minuto' . ($min == 1 ? '' : 's');
    }

    $tiempoEstimado = $pedido['tiempo_estimado'] ?? 15;
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mi Pedido - Mesa <?= esc($id_mesa) ?></title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: Arial, Helvetica, sans-serif;
            background-color: #0b1220;
            color: #e6edf7;
            min-height: 100vh;
        }
        a { text-decoration: none; }

        /* ---- Navbar ---- */
        .navbar {
            display: flex; align-items: center; justify-content: space-between;
            background-color: #0d1526; padding: 16px 32px;
            border-bottom: 1px solid #1c2842;
        }
        .nav-left { display: flex; align-items: center; gap: 14px; }
        .nav-left img { height: 30px; }
        .brand { color: #4aa8ff; font-size: 20px; font-weight: bold; }
        .nav-links { display: flex; gap: 28px; }
        .nav-links a { color: #cdd8ec; font-size: 15px; }
        .nav-links a:hover { color: #4aa8ff; }
        .nav-right { display: flex; align-items: center; gap: 18px; }
        .nav-mesa { color: #cdd8ec; font-size: 14px; }

        /* ---- Layout ---- */
        .contenedor { max-width: 1050px; margin: 0 auto; padding: 30px 20px 60px; }

        .card-encabezado {
            display: flex; align-items: center; justify-content: space-between;
            background-color: #0f1c33; border: 1px solid #1e63b3;
            border-radius: 10px; padding: 20px 24px; margin-bottom: 20px;
        }
        .card-encabezado h2 { color: #4aa8ff; font-size: 20px; margin-bottom: 4px; }
        .card-encabezado p { color: #9fb0cc; font-size: 13px; }
        .estado-badge {
            background-color: #143b66; color: #6fb6ff;
            padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: bold;
        }

        .aviso {
            background-color: #10251d; border-left: 4px solid #2fbf71;
            border-radius: 8px; padding: 16px 20px; margin-bottom: 28px;
        }
        .aviso strong { color: #4fdd93; display: block; margin-bottom: 4px; }
        .aviso span { color: #9fb0cc; font-size: 13px; }

        .titulo-seccion { color: #4aa8ff; font-size: 16px; font-weight: bold; margin-bottom: 16px; }

        /* ---- Progreso ---- */
        .progreso { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 30px; }
        .paso {
            background-color: #0f1a2e; border: 1px solid #24314f;
            border-radius: 8px; padding: 18px; text-align: center;
        }
        .paso.activo { border-color: #2f6fd0; background-color: #10203b; }
        .paso .nombre { font-size: 13px; font-weight: bold; margin-bottom: 6px; }
        .paso .hora { color: #7f90ad; font-size: 13px; }
        .paso.activo .nombre { color: #6fb6ff; }
        .paso.inactivo .nombre { color: #6a7690; }

        /* ---- Stats ---- */
        .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px; }
        .stat {
            background-color: #0f1a2e; border: 1px solid #24314f;
            border-radius: 8px; padding: 22px; text-align: center;
        }
        .stat .label { color: #9fb0cc; font-size: 13px; margin-bottom: 10px; }
        .stat .valor { font-size: 22px; font-weight: bold; }
        .stat .azul { color: #4aa8ff; }
        .stat .naranja { color: #f6a94b; }
        .stat .verde { color: #4fdd93; }

        /* ---- Detalle ---- */
        .detalle-box {
            background-color: #0f1a2e; border: 1px solid #24314f;
            border-radius: 10px; padding: 24px; margin-bottom: 8px;
        }
        .fila-item {
            display: flex; align-items: center; justify-content: space-between;
            background-color: #0d1728; border: 1px solid #1e2b47;
            border-radius: 8px; padding: 14px 18px; margin-bottom: 12px;
        }
        .item-info { display: flex; align-items: center; gap: 14px; }
        .cant {
            background-color: #16263f; color: #6fb6ff;
            font-size: 12px; font-weight: bold; padding: 6px 10px; border-radius: 6px;
        }
        .item-nombre { color: #e6edf7; font-size: 15px; }
        .item-desc { color: #8595b3; font-size: 12px; margin-top: 2px; }
        .item-precio { color: #4fdd93; font-size: 14px; font-weight: bold; }

        .subtotal {
            display: flex; align-items: center; justify-content: space-between;
            padding: 16px 4px 4px; border-top: 1px solid #24314f; margin-top: 6px;
        }
        .subtotal .txt { color: #9fb0cc; font-size: 15px; }
        .subtotal .val { color: #e6edf7; font-size: 16px; font-weight: bold; }

        .vacio { color: #8595b3; text-align: center; padding: 20px; }

        /* ---- Botones ---- */
        .acciones { display: flex; gap: 14px; margin-top: 28px; }
        .btn {
            border: none; border-radius: 8px; padding: 12px 20px;
            font-size: 14px; font-weight: bold; cursor: pointer; color: #fff;
        }
        .btn-azul-claro { background-color: #4aa8ff; }
        .btn-azul-claro:hover { background-color: #3893ec; }
        .btn-azul { background-color: #2f6fd0; }
        .btn-azul:hover { background-color: #285fb4; }
        .btn-rojo { background-color: #e5544a; }
        .btn-rojo:hover { background-color: #d1443a; }

        @media (max-width: 700px) {
            .nav-links { display: none; }
            .progreso, .stats { grid-template-columns: 1fr 1fr; }
            .acciones { flex-wrap: wrap; }
        }
    </style>
</head>
<body>

<nav class="navbar">
    <div class="nav-left">
        <img src="<?= base_url('css/Logo 2.png') ?>" alt="Logo SISPE">
        <span class="brand">Mi Pedido</span>
    </div>
    <div class="nav-links">
        <a href="<?= base_url('menu_digital') ?>">Menu</a>
        <a href="#">Historial</a>
        <a href="#">Ayuda</a>
    </div>
    <div class="nav-right">
        <span class="nav-mesa">Mesa <?= esc($id_mesa) ?></span>
    </div>
</nav>

<main class="contenedor">

    <div class="card-encabezado">
        <div>
            <h2>Pedido #<?= esc($pedido['id_pedido'] ?? '—') ?></h2>
            <p><?= esc($hace) ?></p>
        </div>
        <span class="estado-badge"><?= esc($badge) ?></span>
    </div>

    <div class="aviso">
        <strong>&#10003; Pedido Confirmado</strong>
        <span>Tu pedido ha sido enviado a la cocina y se está preparando. Serás notificado cuando esté listo.</span>
    </div>

    <h3 class="titulo-seccion">Progreso de tu Pedido</h3>
    <div class="progreso">
        <?php
            $pasos = ['Confirmado', 'En Cocina', 'En Preparación', 'Listo'];
            foreach ($pasos as $i => $nombrePaso):
                $n = $i + 1;
                $clase = $n <= $nivel ? 'activo' : 'inactivo';
        ?>
            <div class="paso <?= $clase ?>">
                <div class="nombre"><?= $nombrePaso ?></div>
                <div class="hora"><?= $n <= $nivel ? '&#10003;' : '--:--' ?></div>
            </div>
        <?php endforeach; ?>
    </div>

    <div class="stats">
        <div class="stat">
            <div class="label">Items Pedidos</div>
            <div class="valor azul"><?= (int) $totalItems ?></div>
        </div>
        <div class="stat">
            <div class="label">Tiempo Estimado</div>
            <div class="valor naranja"><?= (int) $tiempoEstimado ?> min</div>
        </div>
        <div class="stat">
            <div class="label">Total</div>
            <div class="valor verde">$<?= number_format($total, 0, ',', '.') ?></div>
        </div>
    </div>

    <div class="detalle-box">
        <h3 class="titulo-seccion">Detalles de tu Pedido</h3>

        <?php if (empty($items)): ?>
            <p class="vacio">Aún no has agregado productos a tu pedido.</p>
        <?php else: ?>
            <?php foreach ($items as $it): ?>
                <div class="fila-item">
                    <div class="item-info">
                        <span class="cant">x<?= (int) $it['cantidad'] ?></span>
                        <div>
                            <div class="item-nombre"><?= esc($it['Productos']) ?></div>
                            <?php if (!empty($it['observaciones']) || !empty($it['descripcion'])): ?>
                                <div class="item-desc"><?= esc($it['observaciones'] ?: $it['descripcion']) ?></div>
                            <?php endif; ?>
                        </div>
                    </div>
                    <span class="item-precio">$<?= number_format($it['valor_venta'] * $it['cantidad'], 0, ',', '.') ?></span>
                </div>
            <?php endforeach; ?>

            <div class="subtotal">
                <span class="txt">Subtotal</span>
                <span class="val">$<?= number_format($total, 0, ',', '.') ?></span>
            </div>
        <?php endif; ?>
    </div>

    <div class="acciones">
        <a href="<?= base_url('menu_digital') ?>" class="btn btn-azul-claro">Añadir más items</a>
        <a href="<?= base_url('menu_digital') ?>" class="btn btn-azul">Ver Menu</a>
        <a href="#" class="btn btn-rojo">Cancelar Pedido</a>
    </div>

</main>

</body>
</html>
