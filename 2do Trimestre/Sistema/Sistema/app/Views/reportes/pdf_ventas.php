<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; color: #333; }
        .header { text-align: center; margin-bottom: 25px; }
        .header h1 { margin-bottom: 5px; color: #374151; }
        .header p { margin: 0; color: #555; font-size: 0.95em; }
        .table-report { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .table-report th, .table-report td { border: 1px solid #ddd; padding: 10px; }
        .table-report th { background: #000000; color: white; text-align: left; }
        .table-report tbody tr:nth-child(odd) { background: #f9fafb; }
        .total-row td { font-weight: bold; background: #eef2ff; }
        .subtotal { text-align: right; }
    </style>
</head>
<body>
    <div class="header">
        <h1><?php echo esc($titulo); ?></h1>
        <p>Fecha: <?php echo esc($fecha); ?> - Hora: <?php echo esc($hora); ?></p>
    </div>

    <table class="table-report">
        <thead>
            <tr>
                <th>ID Factura</th>
                <th>Pedido</th>
                <th>Mesa</th>
                <th>Fecha</th>
                <th>Estado Pedido</th>
                <th>Total</th>
                <th>Métodos de pago</th>
            </tr>
        </thead>
        <tbody>
            <?php if (!empty($facturas)): ?>
                <?php foreach ($facturas as $factura): ?>
                    <tr>
                        <td><?php echo esc($factura['id_factura']); ?></td>
                        <td><?php echo esc($factura['id_pedido']); ?></td>
                        <td><?php echo esc($factura['id_mesa'] ?? '-'); ?></td>
                        <td><?php echo esc(date('d/m/Y H:i', strtotime($factura['Fecha_hora']))); ?></td>
                        <td><?php echo esc($factura['estado_pedido'] ?? 'N/A'); ?></td>
                        <td><?php echo '$' . number_format($factura['Total'], 0, ',', '.'); ?></td>
                        <td><?php echo esc($factura['metodos_pago'] ?? 'Sin pago'); ?></td>
                    </tr>
                <?php endforeach; ?>
                <tr class="total-row">
                    <td colspan="5">Total General</td>
                    <td colspan="2" class="subtotal"><?php echo '$' . number_format($totalGeneral, 0, ',', '.'); ?></td>
                </tr>
            <?php else: ?>
                <tr>
                    <td colspan="7" style="text-align:center; padding: 18px;">No hay ventas registradas.</td>
                </tr>
            <?php endif; ?>

        </tbody>
    </table>
</body>
</html>
