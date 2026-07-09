<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gracias por visitarnos</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: Arial, Helvetica, sans-serif;
            background-color: rgb(116, 111, 111);
            display: flex; justify-content: center; align-items: center;
            min-height: 100vh; padding: 20px;
        }
        .box {
            background-color: white; border-top: 6px solid gold;
            border-radius: 12px; padding: 45px 40px; text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.25); max-width: 420px; width: 100%;
        }
        .box img { height: 60px; margin-bottom: 20px; }
        .check {
            width: 70px; height: 70px; margin: 0 auto 20px; border-radius: 50%;
            background-color: gold; color: #333; font-size: 38px; font-weight: bold;
            display: flex; align-items: center; justify-content: center;
        }
        .box h1 { color: #333; font-size: 24px; margin-bottom: 12px; }
        .box p { color: #777; font-size: 15px; line-height: 1.6; margin-bottom: 8px; }
        .mesa-libre { color: #229a58; font-weight: bold; margin-top: 18px; }
    </style>
</head>
<body>
    <div class="box">
        <div class="check">&#10003;</div>
        <h1>¡Gracias por visitarnos!</h1>
        <p>Esperamos que hayas disfrutado tu experiencia con nosotros.</p>
        <p>¡Te esperamos pronto de nuevo!</p>
        <p class="mesa-libre">La mesa ha quedado libre.</p>
    </div>
</body>
</html>