<?php
/**
 * Vista PDF generica reutilizable para cualquier reporte multitabla.
 * Recibe: $titulo, $fecha, $hora, $rangoTexto, $columnas, $filas,
 *         $totalGeneral, $totalKey
 *
 * Funcion auxiliar para formatear el valor de una celda segun el formato.
 */
if (!function_exists('formatoCelda')) {
    function formatoCelda($valor, $formato)
    {
        if ($valor === null || $valor === '') {
            return '-';
        }
        switch ($formato) {
            case 'money':
                return '$' . number_format((float) $valor, 0, ',', '.');
            case 'fecha':
                $ts = strtotime($valor);
                return $ts ? date('d/m/Y H:i', $ts) : esc($valor);
            case 'siNo':
                return ((int) $valor === 1) ? 'Si' : 'No';
            case 'estadoMesa':
                return ((int) $valor === 1) ? 'Ocupada' : 'Libre';
            case 'auto':
                return is_numeric($valor) ? number_format((float) $valor, 0, ',', '.') : esc($valor);
            default:
                return esc($valor);
        }
    }
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        @page { margin: 25px 30px; }
        body { font-family: Arial, sans-serif; color: #1f2937; font-size: 11px; }
        .header { text-align: center; margin-bottom: 18px; border-bottom: 3px solid #eab566; padding-bottom: 12px; }
        .header h1 { margin: 0 0 6px 0; color: #374151; font-size: 20px; }
        .header p { margin: 2px 0; color: #6b7280; font-size: 11px; }
        .header .rango { color: #b45309; font-weight: bold; }
        .table-report { width: 100%; border-collapse: collapse; margin-top: 14px; }
        .table-report th, .table-report td { border: 1px solid #d1d5db; padding: 7px 8px; }
        .table-report th { background: #111827; color: #ffffff; text-align: left; font-size: 11px; }
        .table-report tbody tr:nth-child(even) { background: #f3f4f6; }
        .table-report td { font-size: 10.5px; }
        .total-row td { font-weight: bold; background: #fff4e0; border-top: 2px solid #eab566; }
        .total-row .subtotal { text-align: right; font-size: 12px; }
        .empty { text-align: center; padding: 22px; color: #9ca3af; font-style: italic; }
        .footer { margin-top: 18px; text-align: center; color: #9ca3af; font-size: 9px; border-top: 1px solid #e5e7eb; padding-top: 8px; }
    </style>
</head>
<body>
    <div class="header">
        <h1><?= esc($titulo) ?></h1>
        <p>Generado el <?= esc($fecha) ?> a las <?= esc($hora) ?></p>
        <?php if (!empty($rangoTexto)): ?>
            <p class="rango"><?= esc($rangoTexto) ?></p>
        <?php endif; ?>
    </div>

    <table class="table-report">
        <thead>
            <tr>
                <?php foreach ($columnas as $col): ?>
                    <th><?= esc($col['label']) ?></th>
                <?php endforeach; ?>
            </tr>
        </thead>
        <tbody>
            <?php if (!empty($filas)): ?>
                <?php foreach ($filas as $fila): ?>
                    <tr>
                        <?php foreach ($columnas as $col): ?>
                            <td><?= formatoCelda($fila[$col['key']] ?? null, $col['formato'] ?? 'text') ?></td>
                        <?php endforeach; ?>
                    </tr>
                <?php endforeach; ?>

                <?php if ($totalGeneral !== null): ?>
                    <tr class="total-row">
                        <td colspan="<?= count($columnas) - 1 ?>">TOTAL GENERAL</td>
                        <td class="subtotal">$<?= number_format((float) $totalGeneral, 0, ',', '.') ?></td>
                    </tr>
                <?php endif; ?>
            <?php else: ?>
                <tr>
                    <td class="empty" colspan="<?= count($columnas) ?>">
                        No se encontraron registros para los criterios seleccionados.
                    </td>
                </tr>
            <?php endif; ?>
        </tbody>
    </table>

    <div class="footer">
        SISPE - Sistema de Gestion para Restaurantes &middot; Reporte generado automaticamente
    </div>
</body>
</html>
