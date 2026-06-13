<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Estado de tu Orden</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f4; text-align: center; padding-top: 50px; }
        .card { background: white; padding: 30px; display: inline-block; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-top: 5px solid gold; }
        .status { font-size: 24px; font-weight: bold; color: orange; margin: 20px 0; text-transform: uppercase; }
        .success-msg { color: green; font-weight: bold; font-size: 18px; }
    </style>
</head>
<body>
<div class="card">
    <div class="success-msg">✔ ¡Registro Exitoso de Pedido!</div>
    <p>Tu orden ha sido enviada directamente a la cocina.</p>
    <hr>
    <p>Estado actual de tu preparación:</p>
    
    <div class="status">
        <?php 
            if($estado == 'pendiente') echo "⏳ En Espera";
            elseif($estado == 'en_preparacion') echo "🍳 En Preparación";
            elseif($estado == 'en_camino') echo "🛵 En Camino";
            elseif($estado == 'entregado') echo "🍽 Pedido Completado";
        ?>
    </div>
    
    <p style="font-size: 12px; color: gray;">Refresca esta página para actualizar el estado.</p>
</div>
</body>
</html>