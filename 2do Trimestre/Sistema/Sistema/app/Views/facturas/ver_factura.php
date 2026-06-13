<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Factura de Venta #<?= $factura['id_factura'] ?></title>
    <link rel="stylesheet" href="<?= base_url('Agregar Factura.Css') ?>">
    <style>
        /* Estilos de impresión: Al salir en papel físico oculta los paneles de control */
        @media print {
            .no-print { display: none !important; }
            body { background: white; color: black; padding: 0; }
            .ticket { border: none; box-shadow: none; width: 100%; margin: 0; }
        }
    </style>
</head>
<body style="background: #f4f4f4; padding: 20px; font-family: monospace;">

<div class="no-print" style="text-align: center; margin-bottom: 20px; background: #fff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); max-width: 420px; margin: 0 auto 20px auto; font-family: sans-serif;">
    <a href="<?= base_url('facturas') ?>" style="padding: 10px 15px; background: #333; color: white; text-decoration: none; font-weight: bold; border-radius: 4px; margin-right: 8px; font-size: 13px;">← Volver</a>
    
    <button onclick="window.print();" style="padding: 10px 15px; background: #007bff; color: white; border: none; font-weight: bold; border-radius: 4px; cursor: pointer; margin-right: 8px; font-size: 13px;">🖨️ Imprimir Factura</button>
    
    <form action="<?= base_url('facturas/eliminar') ?>" method="POST" style="display: inline;">
        <input type="hidden" name="id_factura" value="<?= $factura['id_factura'] ?>">
        <button type="submit" style="padding: 10px 15px; background: #dc3545; color: white; border: none; font-weight: bold; border-radius: 4px; cursor: pointer; font-size: 13px;" onclick="return confirm('¿Estás seguro de que deseas eliminar esta factura de la caja?');">
            🗑️ Eliminar Factura
        </button>
    </form>
</div>

<div class="ticket" style="background: white; max-width: 360px; margin: 0 auto; padding: 20px; border: 1px solid #ccc; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">

    <div style="text-align: center; border-bottom: 1px dashed #333; padding-bottom: 10px; margin-bottom: 10px;">
        <h2 style="margin: 0;">SISTEMA RESTAURANTE</h2>
        <p style="margin: 5px 0; font-size: 12px;">Mesa Seleccionada N° <?= $factura['id_mesa'] ?></p>
        <p style="margin: 5px 0; font-size: 12px;">Fecha: <?= date('d/m/Y h:i A', strtotime($factura['Fecha_hora'])) ?></p>
        <p style="margin: 5px 0; font-weight: bold;">FACTURA N°: <?= $factura['id_factura'] ?></p>
    </div>

    <div style="font-size: 13px; margin-bottom: 10px; border-bottom: 1px dashed #333; padding-bottom: 10px;">
        <p style="margin: 3px 0;"><strong>Cliente:</strong> <?= $factura['nombre_cliente'] ?? 'Consumo Interno' ?></p>
        <p style="margin: 3px 0;"><strong>Cédula:</strong> <?= $factura['cedula_cliente'] ?? 'N/A' ?></p>
        <p style="margin: 3px 0;"><strong>Método Pago:</strong> <?= $factura['metodos_pago'] ?? 'Efectivo' ?></p>
        <p style="margin: 3px 0;"><strong>Pedido Ref:</strong> #<?= $factura['id_pedido'] ?></p>
    </div>

    <table style="width: 100%; font-size: 13px; margin-bottom: 15px;">
        <thead>
            <tr style="border-bottom: 1px solid #eee; text-align: left;">
                <th>Cant.</th>
                <th>Producto</th>
                <th style="text-align: right;">Total</th>
            </tr>
        </thead>
        <tbody>
            <?php 
            $granTotalCalculado = 0; // Acumulador en PHP
            foreach($items as $item): 
                $granTotalCalculado += $item['subtotal']; // Sumamos el valor del plato en vivo
            ?>
                <tr>
                    <td><?= $item['cantidad'] ?>x</td>
                    <td><?= $item['Productos'] ?></td>
                    <td style="text-align: right;">$<?= number_format($item['subtotal'], 0, ',', '.') ?></td>
                </tr>
            <?php endforeach; ?>
        </tbody>
    </table>

    <div style="border-top: 2px double #333; padding-top: 8px; text-align: right; font-size: 16px; font-weight: bold;">
        TOTAL A PAGAR: $<?= number_format($granTotalCalculado, 0, ',', '.') ?>
    </div>

    <div style="text-align: center; margin-top: 25px; font-size: 11px; color: #555;">
        <p>¡Gracias por su compra!</p>
        <p>Desarrollado para software de gestión de pedidos</p>
    </div>
</div>

</body>
</html>