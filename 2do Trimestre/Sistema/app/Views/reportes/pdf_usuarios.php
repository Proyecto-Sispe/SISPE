<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; color: #333; font-size: 12px; }
        .header { text-align: center; margin-bottom: 20px; }
        .header h1 { margin-bottom: 5px; }
        .header p { margin: 0; color: #555; }
        .table-report { width: 100%; border-collapse: collapse; margin-top: 15px; }
        .table-report th, .table-report td { border: 1px solid #ddd; padding: 10px; }
        .table-report th { background: #000000; color: white; text-align: left; }
        .table-report tbody tr:nth-child(odd) { background: #f7f7fc; }
        .table-report td { vertical-align: top; }
        .summary { margin-top: 20px; font-size: 13px; color: #444; }
    </style>
</head>
<body>
    <div class="header">
        <h1><?php echo $titulo; ?></h1>
        <p>Fecha: <?php echo $fecha; ?> - Hora: <?php echo $hora; ?></p>
    </div>
    <table class="table-report">
        <thead>
            <tr>
                <th style="width: 10%">Documento</th>
                <th style="width: 18%">Tipo Doc</th>
                <th style="width: 22%">Nombre</th>
                <th style="width: 18%">Teléfono</th>
                <th style="width: 20%">Correo</th>
                <th style="width: 12%">Rol</th>
            </tr>
        </thead>
        <tbody>
            <?php if (!empty($usuarios)): ?>
                <?php foreach ($usuarios as $usuario): ?>
                    <tr>
                        <td><?php echo esc($usuario['id_usuario']); ?></td>
                        <td><?php echo esc($usuario['nombre_documento']); ?></td>
                        <td><?php echo esc(trim($usuario['Nom1_usu'] . ' ' . ($usuario['Nom2_usu'] ?? '') . ' ' . $usuario['Ape1_usu'] . ' ' . ($usuario['Ape2_usu'] ?? ''))); ?></td>
                        <td><?php echo esc($usuario['Telefono']); ?></td>
                        <td><?php echo esc($usuario['Correo_usu']); ?></td>
                        <td><?php echo esc($usuario['Nom_rol']); ?></td>
                    </tr>
                <?php endforeach; ?>
            <?php else: ?>
                <tr>
                    <td colspan="6" style="text-align:center; padding: 18px;">No hay usuarios activos registrados.</td>
                </tr>
            <?php endif; ?>
        </tbody>
    </table>
    <div class="summary">
        <p>Total de usuarios listados: <?php echo count($usuarios); ?></p>
    </div>

</body>
</html>