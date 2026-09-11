CREATE DATABASE sistema;
USE sistema;

-- =========================================================
-- 1. CREACIÓN DE TABLAS
-- =========================================================

CREATE TABLE IF NOT EXISTS Insumo (
    id_insumo    BIGINT AUTO_INCREMENT PRIMARY KEY,
    nombre       VARCHAR(100)   NOT NULL,
    stock_actual DECIMAL(12,3)  NOT NULL DEFAULT 0,
    stock_minimo DECIMAL(12,3)  NOT NULL DEFAULT 0,
    unidad       VARCHAR(20)    NOT NULL,
    activo       TINYINT(1)     NOT NULL DEFAULT 1,
    CONSTRAINT uq_insumo_nombre UNIQUE (nombre)
);

CREATE TABLE IF NOT EXISTS Menu_Insumo (
    id_menu_insumo BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_menu        INT           NOT NULL,
    id_insumo      BIGINT        NOT NULL,
    cantidad       DECIMAL(12,3) NOT NULL,
    CONSTRAINT uq_menu_insumo UNIQUE (id_menu, id_insumo),
    CONSTRAINT fk_menu_insumo_menu   FOREIGN KEY (id_menu)   REFERENCES Menu(id_menu),
    CONSTRAINT fk_menu_insumo_insumo FOREIGN KEY (id_insumo) REFERENCES Insumo(id_insumo)
);


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

CREATE TABLE password_resets (
  id         INT(11)      NOT NULL AUTO_INCREMENT,
  correo     VARCHAR(120) NOT NULL,
  token      VARCHAR(64)  NOT NULL,   -- hash sha256 del token enviado por correo
  codigo     VARCHAR(6)   NOT NULL,   -- codigo de 6 digitos enviado por correo
  expira     DATETIME     NOT NULL,   -- fecha/hora de expiracion (15 min)
  usado      TINYINT(1)   NOT NULL DEFAULT 0,
  created_at DATETIME     NOT NULL,
  PRIMARY KEY (`id`),
  KEY idx_correo (`correo`),
  KEY idx_token  (`token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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
    Productos VARCHAR(100) NOT NULL,
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
    estado ENUM('pendiente', 'en_preparacion', 'en_camino', 'entregado') DEFAULT 'pendiente',
    prioridad ENUM('normal', 'urgente') DEFAULT 'normal',
    cocinero_asignado INT DEFAULT NULL,
    tiempo_estimado INT DEFAULT 15,
    observaciones TEXT              -- Detalles y adiciones
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

-- =========================================================
-- 2. RESTRICCIONES DE CLAVES FORÁNEAS (FOREIGN KEYS)
-- =========================================================

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

-- =========================================================
-- 3. INSERCIÓN DE DATOS MAESTROS Y BASE
-- =========================================================

INSERT INTO Rol VALUES (1,'Administrador'), (2,'Cocinero'), (3,'Mesero'), (4,'Cliente');

INSERT INTO Tipo_doc VALUES (1,'Cedula de ciudadania',1), (2,'Tarjeta de identidad',1), (3, 'Cedula de extranjeria', 1);

INSERT INTO Persona VALUES
(1002655550,1,'Juan','Carlos','Perez','Lopez',3001234567,'admin@gmail.com','1234',1),
(1053804357,1,'Maria','Fernanda','Gomez','Rodriguez',3019876543,'mesero1@gmail.com','1234',1),
(1053872530,1,'Luis',NULL,'Martinez','Diaz',3024567890,'cocina1@gmail.com','1234',1),
(1152693247,1,'Ana','Sofia','Ramirez','Torres',3035678901,'mesero2@gmail.com','1234',1),
(1070919081,1,'Carlos',NULL,'Hernandez','Morales',3046789012,'cocina2@gmail.com','1234',1),
(1031422939,1,'Victor','Manuel','Solano','Niño',3134890742,'cliente@gmail.com','1234',1);

INSERT INTO Persona_has_Rol VALUES 
(1,1002655550,1), (1,1053804357,3), (1,1053872530,2), (1,1152693247,3), (1,1070919081,2), (1,1031422939,4);

-- MESAS REGISTRADAS (TODAS LIBRES CON ESTADO = 0)
INSERT INTO Mesa (id_Mesa, Capacidad, Ubicacion, Estado) VALUES 
(1, 4, 'Primer Piso', 0),
(2, 2, 'Primer Piso', 0),
(3, 6, 'Segundo Piso', 0),
(4, 4, 'Terraza', 0);

-- CATEGORÍAS DEL MENÚ
INSERT INTO Categoria (id_categoria, nom_categoria) VALUES 
(1, 'Hamburguesas'),
(2, 'Perros Calientes'),
(3, 'Salchipapas'),
(4, 'Entradas'),
(5, 'Pizza'),
(6, 'Burritos'),
(7, 'Nachos y Dorilocos'),
(8, 'Lasagna'),
(9, 'Quesadillas'),
(10, 'Arepas Rellenas'),
(11, 'Mazorcada');

-- =========================================================
-- 4. INSERCIÓN DE PRODUCTOS DESDE LAS FOTOS DE LA CARTA
-- =========================================================

-- --- CATEGORÍA 1: HAMBURGUESAS ---
INSERT INTO Menu (id_menu, Productos, Precio, descripcion, pkfk_id_categoria) VALUES 
(1, 'Hamburguesa Clásica', 16000, 'Carne, queso fundido, papa chip, cebolla caramelizada, tomate, lechuga y salsas', 1),
(2, 'Hamburguesa Soleada', 18000, 'Carne, huevo frito, queso fundido, papa chip, cebolla caramelizada, tomate, lechuga y salsas', 1),
(3, 'Hamburguesa Verano', 18000, 'Carne, rodaja de piña asada, jamón, queso fundido, papa chip, tomate, lechuga y salsas', 1),
(4, 'Hamburguesa Ritmo', 18000, 'Carne, plátano maduro, queso fundido, papa chip, cebolla caramelizada, tomate, lechuga y salsas', 1),
(5, 'Hamburguesa Crispy Bacon', 19000, 'Carne, doble tocineta, queso fundido, papa chip, cebolla caramelizada, tomate, lechuga y salsas', 1),
(6, 'Hamburguesa Paraíso Onion', 19000, 'Carne, aros de cebolla apanados, queso fundido, papa chip, cebolla caramelizada, tomate, lechuga y salsas', 1),
(7, 'Hamburguesa Pasión', 19000, 'Carne, rodajas de pepperoni, queso fundido, papa chip, cebolla caramelizada, tomate, lechuga y salsas', 1),
(8, 'Hamburguesa Paraíso Patacón', 19000, 'Patacón maduro en lugar de pan, carne, jamón, queso fundido, papa chip, cebolla caramelizada, tomate, lechuga y salsas', 1),
(9, 'Hamburguesa Carnal', 19000, 'Carne, pico e gallo, nachos, guacamole, queso fundido, papa chip, cebolla caramelizada, tomate, lechuga y salsas', 1),
(10, 'Hamburguesa Delirio', 20000, 'Carne, chorizo santarrosano, queso fundido, papa chip, cebolla caramelizada, tomate, lechuga y salsas', 1),
(11, 'Hamburguesa Éxtasis', 20000, 'Carne, trozos de costilla de cerdo ahumada sin hueso, queso fundido, papa chip, cebolla caramelizada, tomate, lechuga y salsas', 1),
(12, 'Hamburguesa Queso Fundido', 20000, 'Carne, trozo de queso mozzarella fundido (1.5 cm), papa chip, cebolla caramelizada, tomate, lechuga y salsas', 1),
(13, 'Hamburguesa Doble Tentación', 22000, 'Doble carne, doble queso fundido, papa chip, cebolla caramelizada, tomate, lechuga y salsas', 1),
(14, 'Hamburguesa Pecado', 22000, 'Carne, aros de cebolla, doble tocineta, queso fundido, papa chip, cebolla caramelizada, tomate, lechuga y salsas', 1),
(15, 'Hamburguesa Fusión', 22000, 'Carne de res, pollo apanado, doble queso fundido, papa chip, cebolla caramelizada, tomate, lechuga y salsas', 1),
(16, 'Hamburguesa Triple Placer', 27000, 'Triple carne, triple queso fundido, papa chip, cebolla caramelizada, tomate, lechuga y salsas', 1),
(17, 'Hamburguesa Montañera', 27000, 'Carne, carne desmechada, huevo frito, queso fundido, papa chip, cebolla caramelizada, tomate, lechuga y salsas', 1),
(18, 'Hamburguesa La Divina', 32000, 'Doble carne, trozos de costilla de cerdo ahumado sin hueso, doble tocineta, aros de cebolla, doble queso fundido, papa chip, cebolla caramelizada, tomate, lechuga y salsas', 1);

-- --- CATEGORÍA 3: SALCHIPAPAS Y SUPER PAPAS ---
INSERT INTO Menu (id_menu, Productos, Precio, descripcion, pkfk_id_categoria) VALUES 
(19, 'Salchipapa Tentación', 12000, 'Papas fritas, rodajas de salchicha americana y dos huevos de codorniz', 3),
(20, 'Salchipapa Edén', 12000, 'Papas fritas, rodajas de chorizo santarrosano y dos huevos de codorniz', 3),
(21, 'Salchipapa Sabor Divino', 26000, 'Papas fritas, rodajas de salchicha americana, carne desmechada, pollo desmechado, queso fundido y dos huevos de codorniz', 3),
(22, 'Salchipapa La Divina', 30000, 'Papas fritas, rodajas de salchicha americana, carne desmechada, pollo desmechado, doble tocineta, maíz tierno, queso fundido, huevos de codorniz y aguacate', 3),
(23, 'Super Papas La Divina', 48000, 'Base de papas fritas, trozos de carne de res y pechuga de pollo a la plancha, tocineta, chorizo, lechuga, tomate, queso, maíz tierno, dos huevos de codorniz y salsas', 3);

-- --- CATEGORÍA 4: ENTRADAS ---
INSERT INTO Menu (id_menu, Productos, Precio, descripcion, pkfk_id_categoria) VALUES 
(24, 'Empanaditas de Carne (x6)', 9000, 'Seis empanaditas de carne crujientes', 4),
(25, 'Aros de Cebolla (x6)', 9000, 'Seis aros de cebolla apanados', 4),
(26, 'Croquetas de Yuca (x6)', 10000, 'Seis croquetas de yuca crocantes', 4),
(27, 'Patacones con Hogao (x5)', 13000, 'Cinco patacones crujientes acompañados con hogao tradicional', 4),
(28, 'Nachos con Pico e Gallo', 13000, 'Nachos crujientes acompañados con pico e gallo, guacamole y queso cheddar', 4),
(29, 'Papas con Cheddar y Tocineta', 16000, 'Papas fritas bañadas en salsa de queso cheddar y trozos de tocineta', 4),
(30, 'Nachos con Queso Cheddar y Tocineta', 15000, 'Nachos con abundante queso cheddar fundido y tocineta', 4),
(31, 'Nuggets de Pollo con Papas (x6)', 15000, 'Seis nuggets de pollo apanados acompañados con porción de papas fritas', 4),
(32, 'Canastas de Patacón con Camarones (x3)', 20000, 'Tres canastillas de patacón rellenas de camarones preparados', 4);

-- --- CATEGORÍA 5: PIZZAS (Precios por tamaño Personal) ---
INSERT INTO Menu (id_menu, Productos, Precio, descripcion, pkfk_id_categoria) VALUES 
(33, 'Pizza Pollo con Champiñones', 17000, 'Queso mozzarella, pollo desmechado y champiñones', 5),
(34, 'Pizza Pepperoni', 17000, 'Queso mozzarella y rodajas de pepperoni', 5),
(35, 'Pizza Jamón y Queso', 17000, 'Queso mozzarella y jamón fino', 5),
(36, 'Pizza Pollo y Tocineta', 17000, 'Queso mozzarella, pollo desmechado y tocineta', 5),
(37, 'Pizza Tocineta y Champiñón', 17000, 'Queso mozzarella, tocineta crujiente y champiñones', 5),
(38, 'Pizza Papas al Horno', 17000, 'Queso mozzarella, papas a la francesa fritas cubiertas de salsa cheddar y páprika', 5),
(39, 'Pizza Colombiana', 17000, 'Queso mozzarella, carne molida, chorizo y plátano maduro', 5),
(40, 'Pizza Mexicana', 17000, 'Carne molida, pico e gallo y tostacos picantes', 5),
(41, 'Pizza Primavera', 17000, 'Queso mozzarella, tocineta, maíz tierno y jamón', 5),
(42, 'Pizza Vegetales', 17000, 'Queso mozzarella y mezcla de pimentones, champiñones y cebolla', 5),
(43, 'Pizza BBQ', 17000, 'Queso mozzarella, trozos de costilla de cerdo ahumada con salsa BBQ', 5),
(44, 'Pizza Criolla', 17000, 'Queso mozzarella, carne desmechada y maíz tierno', 5),
(45, 'Pizza Napolitana', 17000, 'Queso mozzarella y tomates frescos cubiertos de orégano', 5),
(46, 'Pizza Ranchera', 17000, 'Carne molida, chorizo y salsa BBQ', 5),
(47, 'Pizza Carbonara', 17000, 'Queso mozzarella, tocineta y champiñones cubiertos en salsa bechamel', 5),
(48, 'Pizza La Divina', 17000, 'Especialidad de la casa: Pollo, carne desmechada y trozos de costilla', 5),
(49, 'Pizza Golden Chicken BBQ', 17000, 'Queso mozzarella, pollo desmechado, maíz tierno y salsa BBQ', 5),
(50, 'Pizza Fresas con Chocolate', 17000, 'Pizza dulce con base de chocolate y fresas frescas', 5),
(51, 'Pizza Hawaiana', 17000, 'Queso mozzarella, jamón y piña', 5),
(52, 'Pizza Pepperoni con Piña', 17000, 'Queso mozzarella, pepperoni y piña', 5),
(53, 'Pizza Veleña', 17000, 'Bocadillo veleño y queso mozzarella melted', 5),
(54, 'Pizza Tropical', 17000, 'Queso mozzarella, uvas pasas, duraznos y cerezas en almíbar', 5);

-- --- CATEGORÍA 6: BURRITOS ---
INSERT INTO Menu (id_menu, Productos, Precio, descripcion, pkfk_id_categoria) VALUES 
(55, 'Burrito El Bendito', 19500, 'Tortilla, carne desmechada, pollo desmechado, lechuga fresca, pico e gallo, queso y guacamole. Acompañado de nachos', 6),
(56, 'Burrito Inmortal', 25000, 'Tortilla, carne desmechada, pollo desmechado, chorizo, tocineta, lechuga fresca, pico e gallo, queso y guacamole. Acompañado de nachos', 6),
(57, 'Burrito Fit', 17500, 'Tortilla, lechuga fresca, maíz tierno, pimentón, champiñón, tomate, pico e gallo y guacamole. Acompañado de nachos', 6),
(58, 'Burrito La Divina', 28000, 'Tortilla, carne desmechada, pollo desmechado, salsa de frijol, carne molida, lechuga fresca, pico e gallo, queso y guacamole. Acompañado de nachos', 6);

-- --- CATEGORÍA 7: NACHOS Y DORILOCOS ---
INSERT INTO Menu (id_menu, Productos, Precio, descripcion, pkfk_id_categoria) VALUES 
(59, 'Dorilocos Carne', 22000, 'Doritos con pico e gallo, guacamole, queso cheddar, salsas, carne y cubierta de queso mozzarella', 7),
(60, 'Dorilocos Pollo', 22000, 'Doritos con pico e gallo, guacamole, queso cheddar, salsas, pollo y cubierta de queso mozzarella', 7),
(61, 'Dorilocos Carne y Pollo', 25000, 'Doritos con pico e gallo, guacamole, queso cheddar, salsas, combinación de carne y pollo, cubierta de mozzarella', 7),
(62, 'Dorilocos Costillas de Cerdo Ahumadas', 24000, 'Doritos con pico e gallo, guacamole, queso cheddar, salsas, costilla ahumada y cubierta de queso mozzarella', 7),
(63, 'Dorilocos La Divina', 28000, 'Doritos/Nachos con salsa de frijol, carne molida, carne desmechada, pico e gallo, queso mozzarella, guacamole y cheddar', 7),
(64, 'Nachos de Maíz Carne', 19000, 'Nachos de maíz con pico e gallo, guacamole, queso cheddar, salsas, carne y cubierta de queso mozzarella', 7),
(65, 'Nachos de Maíz Pollo', 19000, 'Nachos de maíz con pico e gallo, guacamole, queso cheddar, salsas, pollo y cubierta de queso mozzarella', 7),
(66, 'Nachos de Maíz Carne y Pollo', 22000, 'Nachos de maíz con pico e gallo, guacamole, queso cheddar, salsas, carne y pollo', 7),
(67, 'Nachos de Maíz Costillas Ahumadas', 21000, 'Nachos de maíz con pico e gallo, guacamole, queso cheddar, salsas y costilla ahumada', 7),
(68, 'Nachos de Maíz La Divina', 36000, 'Nachos de maíz extra grandes con todas las proteínas, frijol, guacamole, pico e gallo y queso mozzarella', 7);

-- --- CATEGORÍA 8: LASAGNA AL HORNO ---
INSERT INTO Menu (id_menu, Productos, Precio, descripcion, pkfk_id_categoria) VALUES 
(69, 'Lasagna Corazón', 25000, 'Capas de pasta fresca, carne molida en salsa boloñesa, pollo desmechado en salsa bechamel, champiñones, tocineta, jamón, queso gratinado y pan tostado', 8),
(70, 'Lasagna Primavera', 27000, 'Capas de plátano maduro, carne molida en salsa boloñesa, pollo desmechado en salsa bechamel, champiñones, tocineta, jamón, queso gratinado y pan tostado', 8);

-- --- CATEGORÍA 9: QUESADILLAS ---
INSERT INTO Menu (id_menu, Productos, Precio, descripcion, pkfk_id_categoria) VALUES 
(71, 'Quesadilla Carne', 15000, 'Tortilla de harina rellena de queso fundido y carne desmechada', 9),
(72, 'Quesadilla Pollo', 15000, 'Tortilla de harina rellena de queso fundido y pollo desmechado', 9),
(73, 'Quesadilla Carne y Pollo', 17000, 'Tortilla de harina rellena de queso fundido, carne y pollo', 9),
(74, 'Quesadilla Pollo con Champiñones', 17000, 'Tortilla de harina rellena de queso fundido, pollo desmechado y champiñones', 9),
(75, 'Quesadilla Nutella', 14000, 'Tortilla de harina rellena de Nutella derretida', 9),
(76, 'Quesadilla Nutella y Fresas', 15000, 'Tortilla de harina rellena de Nutella y fresas frescas', 9);

-- --- CATEGORÍA 10: AREPAS RELLENAS ---
INSERT INTO Menu (id_menu, Productos, Precio, descripcion, pkfk_id_categoria) VALUES 
(77, 'Arepa Encanto', 14500, 'Carne desmechada, queso y huevo de codorniz', 10),
(78, 'Arepa Cañon', 14500, 'Pollo desmechado, queso y huevo de codorniz', 10),
(79, 'Arepa Furia', 16500, 'Carne desmechada, pollo desmechado, queso y huevo de codorniz', 10),
(80, 'Arepa Valiente', 17500, 'Carne desmechada, chorizo, queso y huevo de codorniz', 10),
(81, 'Arepa La Divina', 18500, 'Carne desmechada, pollo desmechado, queso, jamón y huevo frito', 10);

-- --- CATEGORÍA 11: MAZORCADA ---
INSERT INTO Menu (id_menu, Productos, Precio, descripcion, pkfk_id_categoria) VALUES 
(82, 'Mazorcada Azteca', 26000, 'Maíz tierno, carne desmechada, pollo desmechado, papa chip, queso y salsas', 11),
(83, 'Mazorcada Espartana', 27000, 'Maíz tierno, carne desmechada, pollo desmechado, huevo frito, papa chip, queso y salsas', 11),
(84, 'Mazorcada Suprema', 28000, 'Maíz tierno, carne desmechada, pollo desmechado, plátano maduro, papa chip, queso y salsas', 11),
(85, 'Mazorcada La Divina', 31000, 'Maíz tierno, carne desmechada, pollo desmechado, chorizo, tocineta, papa chip, queso y salsas', 11);

INSERT INTO Insumo (id_insumo, nombre, stock_actual, stock_minimo, unidad, activo) VALUES
-- Carnes y Proteínas
(1, 'Carne de Hamburguesa (150g)', 100.000, 20.000, 'Unidades', 1),
(2, 'Pechuga de Pollo Apanada', 50.000, 10.000, 'Unidades', 1),
(3, 'Pollo Desmechado', 15.000, 3.000, 'Kg', 1),
(4, 'Carne Desmechada', 15.000, 3.000, 'Kg', 1),
(5, 'Carne Molida Boloñesa', 10.000, 2.000, 'Kg', 1),
(6, 'Tocineta Ahumada', 8.000, 2.000, 'Kg', 1),
(7, 'Costilla de Cerdo Ahumada sin Hueso', 10.000, 2.000, 'Kg', 1),
(8, 'Chorizo Santarrosano', 50.000, 10.000, 'Unidades', 1),
(9, 'Salchicha Americana', 100.000, 20.000, 'Unidades', 1),
(10, 'Camarones Limpios', 5.000, 1.000, 'Kg', 1),
(11, 'Nuggets de Pollo', 200.000, 30.000, 'Unidades', 1),
(12, 'Pepperoni', 5.000, 1.000, 'Kg', 1),
(13, 'Jamón Fino', 8.000, 2.000, 'Kg', 1),

-- Lácteos y Quesos
(14, 'Queso Mozzarella', 20.000, 5.000, 'Kg', 1),
(15, 'Salsa de Queso Cheddar', 10.000, 2.000, 'Kg', 1),
(16, 'Queso en Tajadas (Fundido)', 150.000, 30.000, 'Unidades', 1),

-- Vegetales y Verduras
(17, 'Papa a la Francesa (Congelada)', 50.000, 10.000, 'Kg', 1),
(18, 'Lechuga Fresca', 10.000, 2.000, 'Kg', 1),
(19, 'Tomate', 15.000, 3.000, 'Kg', 1),
(20, 'Cebolla Caramelizada', 8.000, 2.000, 'Kg', 1),
(21, 'Cebolla Cabezona (Aros/Pico e gallo)', 10.000, 2.000, 'Kg', 1),
(22, 'Champiñones Frescos', 5.000, 1.000, 'Kg', 1),
(23, 'Maíz Tierno', 12.000, 3.000, 'Kg', 1),
(24, 'Plátano Maduro', 30.000, 5.000, 'Unidades', 1),
(25, 'Yuca para Croquetas', 10.000, 2.000, 'Kg', 1),
(26, 'Aguacate / Guacamole', 10.000, 2.000, 'Kg', 1),

-- Panadería, Tortillas y Frutos
(27, 'Pan de Hamburguesa', 120.000, 20.000, 'Unidades', 1),
(28, 'Tortilla de Harina (Burrito/Quesadilla)', 100.000, 20.000, 'Unidades', 1),
(29, 'Nachos / Tostacos', 15.000, 3.000, 'Kg', 1),
(30, 'Paquete Doritos', 50.000, 10.000, 'Unidades', 1),
(31, 'Arepa Blanca para Rellenar', 60.000, 15.000, 'Unidades', 1),
(32, 'Masa / Base de Pizza Personal', 50.000, 10.000, 'Unidades', 1),
(33, 'Plátano para Canastillas Patacón', 40.000, 10.000, 'Unidades', 1),
(34, 'Pasta Lasagna (Láminas)', 100.000, 20.000, 'Unidades', 1),

-- Dulces y Frutas
(35, 'Piña en Almíbar / Asada', 8.000, 2.000, 'Kg', 1),
(36, 'Fresas Frescas', 5.000, 1.000, 'Kg', 1),
(37, 'Nutella / Crema de Avellana', 5.000, 1.000, 'Kg', 1),
(38, 'Bocadillo Veleño', 5.000, 1.000, 'Kg', 1),

-- Varios, Huevos y Salsas
(39, 'Huevos de Codorniz', 200.000, 40.000, 'Unidades', 1),
(40, 'Huevos de Gallina', 150.000, 30.000, 'Unidades', 1),
(41, 'Papa Chip (Fritura crujiente)', 10.000, 2.000, 'Kg', 1),
(42, 'Salsa BBQ', 8.000, 2.000, 'Kg', 1),
(43, 'Salsa Bechamel / Casa', 10.000, 2.000, 'Kg', 1),
(44, 'Hogao Criollo', 8.000, 2.000, 'Kg', 1),
(45, 'Salsa de Frijol Refrito', 10.000, 2.000, 'Kg', 1);

-- =========================================================
-- 5. TRIGGERS
-- =========================================================

DELIMITER $$

-- Trigger 1: Cambiar estado de la mesa a ocupada (1) al hacer pedido
CREATE TRIGGER trg_ocupar_mesa
AFTER INSERT ON Pedido
FOR EACH ROW
BEGIN
    UPDATE Mesa SET Estado = 1 WHERE id_Mesa = NEW.id_mesa;
END$$

-- Trigger 2: Calcular total de factura desde el detalle del pedido
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

-- Trigger 3: Generar notificación automática para el personal de cocina
CREATE TRIGGER trg_notificacion_nuevo_pedido
AFTER INSERT ON Pedido
FOR EACH ROW
BEGIN
    INSERT INTO Notificaciones(tipo, mensaje, id_mesa, id_pedido, destinatario_rol)
    VALUES('nuevo_pedido', CONCAT('Nuevo pedido en mesa ', NEW.id_mesa), NEW.id_mesa, NEW.id_pedido, 2);
END$$

DELIMITER ;

-- =========================================================
-- 6. PROCEDIMIENTOS ALMACENADOS
-- =========================================================

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
    
    SELECT Estado INTO v_estado_mesa FROM Mesa WHERE id_Mesa = p_id_mesa;
    
    IF v_estado_mesa = 1 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Mesa ocupada. No se puede escanear en este momento.';
    ELSE
        INSERT INTO Sesion_Mesa (id_mesa, codigo_acceso, nombre_cliente, cedula_cliente, activa)
        VALUES (p_id_mesa, SUBSTRING(MD5(RAND()), 1, 6), p_nombre, p_cedula, 1);
        
        SET v_id_sesion = LAST_INSERT_ID();
        
        INSERT INTO Pedido (id_mesa, mesero_tipo_doc, mesero_id_usuario, cliente_tipo_doc, cliente_id_usuario, id_sesion_qr, estado)
        VALUES (p_id_mesa, NULL, NULL, NULL, NULL, v_id_sesion, 'pendiente');
        
        SET p_id_pedido_nuevo = LAST_INSERT_ID();
        
        INSERT INTO Factura (id_pedido, Total) VALUES (p_id_pedido_nuevo, 0.0);
    END IF;
END$$

CREATE PROCEDURE DespacharPedidoYLiberarMesa(
    IN p_id_pedido INT
)
BEGIN
    DECLARE v_id_mesa INT;
    DECLARE v_id_sesion INT;
    
    SELECT id_mesa, id_sesion_qr INTO v_id_mesa, v_id_sesion FROM Pedido WHERE id_pedido = p_id_pedido;
    
    UPDATE Pedido SET estado = 'entregado' WHERE id_pedido = p_id_pedido;
    UPDATE Sesion_Mesa SET activa = 0, fecha_fin = NOW() WHERE id_sesion = v_id_sesion;
    UPDATE Mesa SET Estado = 0 WHERE id_Mesa = v_id_mesa;
END$$

CREATE PROCEDURE EliminarMesaSegura(
    IN p_id_mesa INT
)
BEGIN
    DELETE FROM Factura WHERE id_pedido IN (SELECT id_pedido FROM Pedido WHERE id_mesa = p_id_mesa);
    DELETE FROM Detalle_Pedido WHERE id_pedido IN (SELECT id_pedido FROM Pedido WHERE id_mesa = p_id_mesa);
    DELETE FROM Pedido WHERE id_mesa = p_id_mesa;
    DELETE FROM Sesion_Mesa WHERE id_mesa = p_id_mesa;
    DELETE FROM Mesa WHERE id_Mesa = p_id_mesa;
END$$

DELIMITER ;


USE sistema;

-- 1. Foto del producto (se guarda la ruta, ej: /uploads/menu/xxxx.jpg)
ALTER TABLE Menu ADD COLUMN foto VARCHAR(255) NULL;

-- 2. El pedido queda "bloqueado" para edición una vez el cliente paga
ALTER TABLE Pedido ADD COLUMN confirmado TINYINT(1) NOT NULL DEFAULT 0;

-- 3. Catálogo de adiciones (extras que se le pueden agregar a cualquier producto)
CREATE TABLE IF NOT EXISTS Adicion (
    id_adicion INT AUTO_INCREMENT PRIMARY KEY,
    nombre     VARCHAR(80)    NOT NULL,
    precio     DECIMAL(10,2)  NOT NULL DEFAULT 0
);

-- 4. Relación: qué adiciones tiene cada línea del pedido
CREATE TABLE IF NOT EXISTS Detalle_Pedido_Adicion (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    id_detalle  INT NOT NULL,
    id_adicion  INT NOT NULL,
    cantidad    INT NOT NULL DEFAULT 1,
    CONSTRAINT fk_dpa_detalle FOREIGN KEY (id_detalle) REFERENCES Detalle_Pedido(id_detalle) ON DELETE CASCADE,
    CONSTRAINT fk_dpa_adicion FOREIGN KEY (id_adicion) REFERENCES Adicion(id_adicion)
);

-- 5. Métodos de pago que pediste: Efectivo, Tarjeta, Nequi
INSERT INTO Metodo_pago (id_pago, Tipo_pago) VALUES
    (1, 'Efectivo'),
    (2, 'Tarjeta'),
    (3, 'Nequi');

-- 6. Adiciones de ejemplo (ajusta nombres y precios como quieras desde el panel admin más adelante)
INSERT INTO Adicion (nombre, precio) VALUES
    ('Queso extra', 3000),
    ('Tocineta extra', 4000),
    ('Sin cebolla', 0),
    ('Papas grandes', 5000),
    ('Salsa BBQ extra', 1500);