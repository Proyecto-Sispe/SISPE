CREATE DATABASE sistema;
USE sistema;

CREATE TABLE Rol (
    idRol INT NOT NULL,
    Nom_rol VARCHAR(45) NOT NULL,
    PRIMARY KEY (idRol)
);

CREATE TABLE Tipo_doc (
    id_doc INT NOT NULL,
    tipo_doc VARCHAR(45) NOT NULL,
    estado TINYINT NOT NULL,
    PRIMARY KEY(id_doc)
);

CREATE TABLE Persona (
    id_usuario INT NOT NULL,
    pkfk_Tipo_doc INT NOT NULL,
    Nom1_usu VARCHAR(20) NOT NULL,
    Nom2_usu VARCHAR(20),
    Ape1_usu VARCHAR(20) NOT NULL,
    Ape2_usu VARCHAR(20),
    Telefono BIGINT NOT NULL,
    Correo_usu VARCHAR(45) UNIQUE,
    Password VARCHAR(255) NOT NULL,
    estado TINYINT DEFAULT 1,
    PRIMARY KEY (id_usuario, pkfk_Tipo_doc)
);

CREATE TABLE Persona_has_Rol (
    pkfk_Tipo_doc INT NOT NULL,
    pkfk_id_usuario INT NOT NULL,
    pkfk_idRol INT NOT NULL,
    PRIMARY KEY (pkfk_id_usuario, pkfk_Tipo_doc, pkfk_idRol)
);

CREATE TABLE Mesa (
    id_Mesa INT NOT NULL,
    Capacidad MEDIUMINT NOT NULL,
    Ubicacion VARCHAR(50) NOT NULL,
    Estado TINYINT NOT NULL DEFAULT 0, -- 0: Libre, 1: Ocupada
    PRIMARY KEY(id_Mesa)
);

CREATE TABLE Categoria (
    id_categoria INT NOT NULL,
    nom_categoria VARCHAR(100) NOT NULL,
    PRIMARY KEY(id_categoria)
);

CREATE TABLE Menu (
    id_menu INT NOT NULL,
    Productos VARCHAR(50) NOT NULL,
    Precio FLOAT NOT NULL,
    descripcion TEXT NOT NULL,
    pkfk_id_categoria INT NOT NULL,
    PRIMARY KEY(id_menu)
);

CREATE TABLE Sesion_Mesa (
    id_sesion INT AUTO_INCREMENT PRIMARY KEY,
    id_mesa INT NOT NULL,
    codigo_acceso VARCHAR(6) NOT NULL,
    nombre_cliente VARCHAR(100) NOT NULL, -- Nombre digitado en el QR
    cedula_cliente INT NOT NULL,          -- Cédula digitada en el QR
    fecha_inicio DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_fin DATETIME NULL,
    activa TINYINT DEFAULT 1
);

CREATE TABLE Pedido (
    id_pedido INT AUTO_INCREMENT PRIMARY KEY,
    id_mesa INT NOT NULL,
    mesero_tipo_doc INT NULL,       -- NULL porque el cliente pide solo desde el QR
    mesero_id_usuario INT NULL,     -- NULL
    cliente_tipo_doc INT NULL,      -- NULL para no obligarlo a estar en la tabla Persona
    cliente_id_usuario INT NULL,    -- NULL
    id_sesion_qr INT NULL,          -- Enlace directo a la Sesión activa del QR
    fecha_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('pendiente', 'en_preparacion', 'en_camino', 'entregado') DEFAULT 'pendiente', -- Añadidos tus estados reales
    prioridad ENUM('normal', 'urgente') DEFAULT 'normal',
    cocinero_asignado INT DEFAULT NULL,
    tiempo_estimado INT DEFAULT 15,
    observaciones TEXT              -- Aquí caen los detalles de las adiciones
);

CREATE TABLE Detalle_Pedido (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido INT NOT NULL,
    id_menu INT NOT NULL,
    cantidad INT NOT NULL,
    valor_venta FLOAT NOT NULL,
    observaciones TEXT
);

CREATE TABLE Factura (
    id_factura INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido INT NOT NULL UNIQUE,
    Fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    Total FLOAT NOT NULL DEFAULT 0.0
);

CREATE TABLE Metodo_pago (
    id_pago INT NOT NULL,
    Tipo_pago VARCHAR(45) NOT NULL,
    PRIMARY KEY(id_pago)
);

CREATE TABLE Factura_has_Metodo_pago (
    pkfk_n_factura INT NOT NULL,
    pkfk_metodo_pago INT NOT NULL,
    monto FLOAT NOT NULL,
    PRIMARY KEY (pkfk_n_factura, pkfk_metodo_pago)
);

CREATE TABLE Notificaciones (
    id_notificacion INT AUTO_INCREMENT PRIMARY KEY,
    tipo ENUM('pedido_listo', 'nuevo_pedido', 'pedido_urgente') NOT NULL,
    mensaje TEXT NOT NULL,
    id_mesa INT,
    id_pedido INT,
    leida TINYINT DEFAULT 0,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    destinatario_rol INT
);

ALTER TABLE Persona 
ADD CONSTRAINT fk_persona_tipo_doc 
FOREIGN KEY (pkfk_Tipo_doc) 
REFERENCES Tipo_doc(id_doc);

ALTER TABLE Persona_has_Rol
ADD CONSTRAINT fk_phr_persona
FOREIGN KEY (pkfk_id_usuario, pkfk_Tipo_doc) 
REFERENCES Persona(id_usuario, pkfk_Tipo_doc);

ALTER TABLE Persona_has_Rol 
ADD CONSTRAINT fk_phr_rol 
FOREIGN KEY (pkfk_idRol) 
REFERENCES Rol(idRol);

ALTER TABLE Menu 
ADD CONSTRAINT fk_menu_categoria 
FOREIGN KEY (pkfk_id_categoria) 
REFERENCES Categoria(id_categoria);

ALTER TABLE Pedido 
ADD CONSTRAINT fk_pedido_mesa 
FOREIGN KEY (id_mesa) 
REFERENCES Mesa(id_Mesa);

ALTER TABLE Pedido 
ADD CONSTRAINT fk_pedido_sesion 
FOREIGN KEY (id_sesion_qr) 
REFERENCES Sesion_Mesa(id_sesion);

ALTER TABLE Detalle_Pedido 
ADD CONSTRAINT fk_detalle_pedido 
FOREIGN KEY (id_pedido) 
REFERENCES Pedido(id_pedido) ON DELETE CASCADE;

ALTER TABLE Detalle_Pedido 
ADD CONSTRAINT fk_detalle_menu 
FOREIGN KEY (id_menu) 
REFERENCES Menu(id_menu);

ALTER TABLE Factura 
ADD CONSTRAINT fk_factura_pedido 
FOREIGN KEY (id_pedido) 
REFERENCES Pedido(id_pedido) ON DELETE CASCADE;

ALTER TABLE Factura_has_Metodo_pago 
ADD CONSTRAINT fk_fmp_factura 
FOREIGN KEY (pkfk_n_factura) 
REFERENCES Factura(id_factura);

ALTER TABLE Factura_has_Metodo_pago 
ADD CONSTRAINT fk_fmp_metodo 
FOREIGN KEY (pkfk_metodo_pago) 
REFERENCES Metodo_pago(id_pago);

ALTER TABLE Notificaciones 
ADD CONSTRAINT fk_noti_mesa 
FOREIGN KEY (id_mesa) 
REFERENCES Mesa(id_Mesa);

ALTER TABLE Notificaciones 
ADD CONSTRAINT fk_noti_pedido 
FOREIGN KEY (id_pedido) 
REFERENCES Pedido(id_pedido);

ALTER TABLE Notificaciones 
ADD CONSTRAINT fk_noti_rol 
FOREIGN KEY (destinatario_rol) 
REFERENCES Rol(idRol);

ALTER TABLE Sesion_Mesa 
ADD CONSTRAINT fk_sesion_mesa_ref 
FOREIGN KEY (id_mesa) 
REFERENCES Mesa(id_Mesa);

INSERT INTO Rol VALUES (1,'Administrador'), (2,'Cocinero'), (3,'Mesero'), (4,'Cliente');
INSERT INTO Tipo_doc VALUES (1,'Cedula de ciudadania',1), (2,'Tarjeta de identidad',1), (3, 'Cedula de extranjeria', 1);

INSERT INTO Persona VALUES
(1002655550,1,'Juan','Carlos','Perez','Lopez',3001234567,'admin@gmail.com','1234',1),
(1053804357,1,'Maria','Fernanda','Gomez','Rodriguez',3019876543,'mesero1@gmail.com','1234',1),
(1053872530,1,'Luis',NULL,'Martinez','Diaz',3024567890,'cocina1@gmail.com','1234',1),
(1152693247,1,'Ana','Sofia','Ramirez','Torres',3035678901,'mesero2@gmail.com','1234',1),
(1070919081,1,'Carlos',NULL,'Hernandez','Morales',3046789012,'cocina2@gmail.com','1234',1),
(1031422939,1,'Victor','Manuel','Solano','Niño',3134890742,'cliente@gmail.com','1234',1);

INSERT INTO Persona_has_Rol VALUES (1,1002655550,1), (1,1053804357,3), (1,1053872530,2), (1,1152693247,3), (1,1070919081,2), (1,1031422939,4);
INSERT INTO Mesa VALUES (1,4,'Primer Piso',0), (2,2,'Primer Piso',0), (3,6,'Segundo Piso',0), (4,4,'Terraza',0);
INSERT INTO Categoria VALUES (1,'Hamburguesas'), (2,'Perros Calientes'), (3,'Salchipapa');
INSERT INTO Menu VALUES (1,'Hamburguesa Divina',14000,'Carne, queso fundido y vegetales',1), (2,'Hamburguesa Soleada',16000,'Carne, huevo y queso fundido',1), (3,'Perro Nube',13000,'Salchicha y queso',2), (4,'Salchipapa Tentacion',10000,'Papas fritas y salchicha',3);

DELIMITER $$

-- Trigger 1: Cuando el cliente hace el pedido, la mesa se marca como ocupada (1)
CREATE TRIGGER trg_ocupar_mesa
AFTER INSERT ON Pedido
FOR EACH ROW
BEGIN
    UPDATE Mesa SET Estado = 1 WHERE id_Mesa = NEW.id_mesa;
END$$

-- Trigger 2: Cuando se genera la factura, se liquida el total sumando el detalle del pedido
CREATE TRIGGER trg_total_factura
BEFORE INSERT ON Factura
FOR EACH ROW
BEGIN
    SET NEW.Total = (
        SELECT IFNULL(SUM(valor_venta * cantidad), 0)
        FROM Detalle_Pedido
        WHERE id_pedido = NEW.id_pedido
    );
END$$

-- Trigger 3: Envía la alerta de notificación de forma automática a la Cocina (Rol 2)
CREATE TRIGGER trg_notificacion_nuevo_pedido
AFTER INSERT ON Pedido
FOR EACH ROW
BEGIN
    INSERT INTO Notificaciones(tipo, mensaje, id_mesa, id_pedido, destinatario_rol)
    VALUES('nuevo_pedido', CONCAT('Nuevo pedido en mesa ', NEW.id_mesa), NEW.id_mesa, NEW.id_pedido, 2);
END$$

DELIMITER ;

-- Procedimientos RegistrarClienteYCrearPedido, DespacharPedidoYLiberarMesa y EliminarMesaSegura

DELIMITER $$

CREATE PROCEDURE RegistrarClienteYCrearPedido(
    IN p_id_mesa INT,
    IN p_nombre VARCHAR(100),
    IN p_cedula INT,
    OUT p_id_pedido_nuevo INT
)
BEGIN
    DECLARE v_estado_mesa TINYINT;
    DECLARE v_id_sesion INT;
    
    -- Verificar el estado de la mesa
    SELECT Estado INTO v_estado_mesa FROM Mesa WHERE id_Mesa = p_id_mesa;
    
    IF v_estado_mesa = 1 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Mesa ocupada. No se puede escanear en este momento.';
    ELSE
        -- 1. Crear la Sesión QR de este cliente temporal
        INSERT INTO Sesion_Mesa (id_mesa, codigo_acceso, nombre_cliente, cedula_cliente, activa)
        VALUES (p_id_mesa, SUBSTRING(MD5(RAND()), 1, 6), p_nombre, p_cedula, 1);
        
        SET v_id_sesion = LAST_INSERT_ID();
        
        -- 2. Crear el Pedido Maestro asignando los valores nulos para el personal interno
        INSERT INTO Pedido (id_mesa, mesero_tipo_doc, mesero_id_usuario, cliente_tipo_doc, cliente_id_usuario, id_sesion_qr, estado)
        VALUES (p_id_mesa, NULL, NULL, NULL, NULL, v_id_sesion, 'pendiente');
        
        SET p_id_pedido_nuevo = LAST_INSERT_ID();
        
        -- 3. Generar la Factura en blanco en el panel
        INSERT INTO Factura (id_pedido, Total) VALUES (p_id_pedido_nuevo, 0.0);
    END IF;
END$$

DELIMITER ;


DELIMITER $$

CREATE PROCEDURE DespacharPedidoYLiberarMesa(
    IN p_id_pedido INT
)
BEGIN
    DECLARE v_id_mesa INT;
    DECLARE v_id_sesion INT;
    
    -- Consultar la mesa y sesión asociadas al pedido
    SELECT id_mesa, id_sesion_qr INTO v_id_mesa, v_id_sesion FROM Pedido WHERE id_pedido = p_id_pedido;
    
    -- 1. Cambiar el estado del pedido al último nivel
    UPDATE Pedido SET estado = 'entregado' WHERE id_pedido = p_id_pedido;
    
    -- 2. Desactivar la sesión del QR
    UPDATE Sesion_Mesa SET activa = 0, fecha_fin = NOW() WHERE id_sesion = v_id_sesion;
    
    -- 3. Liberar la mesa para nuevos comensales
    UPDATE Mesa SET Estado = 0 WHERE id_Mesa = v_id_mesa;
END$$

DELIMITER ;


DELIMITER $$

CREATE PROCEDURE EliminarMesaSegura(
    IN p_id_mesa INT
)
BEGIN
    -- 1. Borramos las facturas asociadas a los pedidos de esa mesa
    DELETE FROM Factura WHERE id_pedido IN (SELECT id_pedido FROM Pedido WHERE id_mesa = p_id_mesa);
    
    -- 2. Borramos los detalles de los pedidos de esa mesa
    DELETE FROM Detalle_Pedido WHERE id_pedido IN (SELECT id_pedido FROM Pedido WHERE id_mesa = p_id_mesa);
    
    -- 3. Borramos los pedidos de esa mesa
    DELETE FROM Pedido WHERE id_mesa = p_id_mesa;
    
    -- 4. Borramos las sesiones de QR de esa mesa
    DELETE FROM Sesion_Mesa WHERE id_mesa = p_id_mesa;
    
    -- 5. Finalmente, eliminamos la mesa de la tabla maestra
    DELETE FROM Mesa WHERE id_Mesa = p_id_mesa;
END$$

DELIMITER ;

