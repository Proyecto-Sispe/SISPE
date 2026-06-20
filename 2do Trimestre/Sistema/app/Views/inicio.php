<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="<?php echo base_url('css/Logo 2.png'); ?>" type="image/png">
    <link rel="stylesheet" href="<?php echo base_url('css/inicio.css'); ?>">
    <title>SISPE - Sistema de Gestión para Restaurantes</title>
</head>
<body>

<nav>
    <ul class="menu">
        <li class="logo">
            <img src="<?php echo base_url('css/Logo 2.png'); ?>" alt="Logo SISPE">
        </li>
        <li><a href="<?php echo base_url('/'); ?>">Inicio</a></li>
        <li><a href="#modulos">Módulos</a></li>
        <li><a href="#nosotros">Nosotros</a></li>
        <li><a href="<?php echo base_url('registro'); ?>">Registro</a></li>
        <li class="right"><a href="<?php echo base_url('login'); ?>">Iniciar Sesión</a></li>
    </ul>
</nav>

<section class="hero">
    <div class="hero-contenido">
        <h1>Bienvenido a SISPE</h1>
        <p>
            El Sistema de Gestión para Restaurantes que centraliza tus mesas, menú digital,
            pedidos en tiempo real, facturación y reportes en un solo lugar. Optimiza la
            operación de tu negocio y mejora la experiencia de tus clientes.
        </p>
        <div class="botones">
            <a href="<?php echo base_url('login'); ?>" class="btn btn-principal">Iniciar Sesión</a>
            <a href="<?php echo base_url('registro'); ?>" class="btn btn-secundario">Crear Cuenta</a>
        </div>
    </div>
    <div class="hero-icono">
        <img src="<?php echo base_url('css/Logo.png'); ?>" alt="Icono SISPE">
    </div>
</section>

<section class="modulos" id="modulos">
    <h2>¿Qué puedes hacer con SISPE?</h2>
    <div class="contenedor-modulos">

        <div class="card">
            <h3>Control de Mesas</h3>
            <p>Gestiona la disponibilidad, capacidad y ubicación de cada mesa, con acceso rápido por código QR.</p>
        </div>

        <div class="card">
            <h3>Menú Digital</h3>
            <p>Organiza productos, categorías y precios. Tus clientes consultan el menú desde su celular.</p>
        </div>

        <div class="card">
            <h3>Pedidos en Tiempo Real</h3>
            <p>Recibe y controla los pedidos al instante con un panel de cocina tipo semáforo de estados.</p>
        </div>

        <div class="card">
            <h3>Facturación</h3>
            <p>Genera facturas, gestiona pagos y mantén el historial de ventas siempre disponible.</p>
        </div>

        <div class="card">
            <h3>Gestión de Personas</h3>
            <p>Administra clientes, meseros, cocineros y administradores con roles y permisos.</p>
        </div>

        <div class="card">
            <h3>Reportes en PDF</h3>
            <p>Genera reportes de ventas, productos y usuarios para tomar mejores decisiones.</p>
        </div>

    </div>
</section>

<section class="modulos" id="nosotros">
    <h2>Sobre SISPE</h2>
    <div class="contenedor-modulos" style="grid-template-columns: 1fr;">
        <div class="card">
            <p>
                SISPE es un proyecto académico desarrollado para digitalizar y simplificar la
                administración de restaurantes. Une en una sola plataforma todas las áreas clave
                del servicio: desde que el cliente escanea el QR de su mesa hasta la entrega de su
                factura. Inicia sesión para acceder a tu panel según tu rol, o crea una cuenta
                para comenzar.
            </p>
        </div>
    </div>
</section>

<footer class="footer">
    <div class="footer-contenido">
        <div class="footer-izq">
            <h3>SISPE</h3>
            <p>Sistema de Gestión para Restaurantes</p>
        </div>
        <div class="footer-der">
            <p>© <?php echo date('Y'); ?> SISPE. Todos los derechos reservados.</p>
        </div>
    </div>
</footer>

</body>
</html>