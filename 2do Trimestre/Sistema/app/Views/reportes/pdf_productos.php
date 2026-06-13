<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            color: #333;
            background: white;
        }

        .contenedor {
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }

        .encabezado {
            border-bottom: 3px solid #000000;
            padding-bottom: 15px;
            margin-bottom: 20px;
            text-align: center;
        }

        .encabezado h1 {
            font-size: 28px;
            color: #000000;
            margin-bottom: 10px;
        }

        .info-reporte {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: #666;
            margin-bottom: 20px;
        }

        .tabla-productos {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        .tabla-productos thead {
            background-color: #000000;
            color: white;
        }

        .tabla-productos th {
            padding: 12px;
            text-align: left;
            font-weight: bold;
            border: 1px solid #ddd;
        }

        .tabla-productos td {
            padding: 12px;
            border: 1px solid #ddd;
            font-size: 12px;
        }

        .tabla-productos tbody tr:nth-child(odd) {
            background-color: #f9f9f9;
        }

        .tabla-productos tbody tr:hover {
            background-color: #f0f0f0;
        }

        .categoria {
            background-color: #e8eaf6;
            font-weight: bold;
            color: #000000;
        }

        .precio {
            text-align: right;
            font-weight: bold;
            color: #27ae60;
        }

        .descripcion {
            color: #777;
            font-size: 11px;
            max-width: 300px;
        }

        .pie-pagina {
            margin-top: 30px;
            text-align: center;
            font-size: 11px;
            color: #999;
            border-top: 1px solid #ddd;
            padding-top: 15px;
        }

        .resumen {
            margin-top: 20px;
            padding: 15px;
            background-color: #f0f4ff;
            border-left: 4px solid #c2c2c2;
            border-radius: 4px;
        }

        .resumen p {
            margin: 5px 0;
            font-size: 13px;
        }

        .total-productos {
            font-weight: bold;
            font-size: 14px;
            color: #252627;
        }
    </style>
</head>
<body>
    <div class="contenedor">
        <div class="encabezado">
            <h1><?php echo $titulo; ?></h1>
            <div class="info-reporte">
                <span><strong>Fecha:</strong> <?php echo $fecha; ?></span>
                <span><strong>Hora:</strong> <?php echo $hora; ?></span>
                <span><strong>Sistema:</strong> SISPE</span>
            </div>
        </div>

        <table class="tabla-productos">
            <thead>
                <tr>
                    <th style="width: 5%;">ID</th>
                    <th style="width: 15%;">Categoría</th>
                    <th style="width: 30%;">Producto</th>
                    <th style="width: 35%;">Descripción</th>
                    <th style="width: 15%; text-align: right;">Precio</th>
                </tr>
            </thead>
            <tbody>
                <?php 
                $categoria_anterior = '';
                $total_productos = 0;
                
                if (!empty($productos)):
                    foreach ($productos as $producto):
                        $total_productos++;
                        
                        // Mostrar fila de categoría si cambió
                        if ($categoria_anterior !== $producto['nom_categoria']):
                            if ($categoria_anterior !== ''):
                                echo '<tr style="height: 5px;"><td colspan="5"></td></tr>';
                            endif;
                            $categoria_anterior = $producto['nom_categoria'];
                        endif;
                ?>
                <tr>
                    <td><?php echo $producto['id_menu']; ?></td>
                    <td class="categoria"><?php echo $producto['nom_categoria']; ?></td>
                    <td><strong><?php echo $producto['Productos']; ?></strong></td>
                    <td class="descripcion"><?php echo $producto['descripcion']; ?></td>
                    <td class="precio">$<?php echo number_format($producto['Precio'], 0, ',', '.'); ?></td>
                </tr>
                <?php 
                    endforeach;
                else:
                ?>
                <tr>
                    <td colspan="5" style="text-align: center; padding: 20px;">
                        <em>No hay productos registrados en la base de datos</em>
                    </td>
                </tr>
                <?php endif; ?>
            </tbody>
        </table>

        <div class="resumen">
            <p class="total-productos"> Total de Productos: <?php echo $total_productos; ?></p>
        </div>

        <div class="pie-pagina">
            <p>Este reporte fue generado automáticamente por el Sistema de Gestión para Restaurantes (SISPE)</p>
            <p>© 2026 SISPE - Todos los derechos reservados</p>
        </div>
    </div>
</body>
</html>
