-- =====================================================================
--  DATOS DE EJEMPLO PARA LOS REPORTES DEL SISTEMA
--  Ejecutar DESPUES de sistema.sql (que ya crea Rol, Tipo_doc, Persona,
--  Persona_has_Rol, Mesa, Categoria y Menu).
--
--  IMPORTANTE - ORDEN POR LOS TRIGGERS:
--    * trg_total_factura   -> calcula Factura.Total desde Detalle_Pedido,
--                             por eso Detalle_Pedido SE INSERTA ANTES que Factura.
--    * trg_ocupar_mesa     -> al insertar Pedido pone la Mesa en Ocupada (1).
--    * trg_notificacion... -> crea filas en Notificaciones automaticamente.
--  Al final se corrigen los estados reales de las mesas.
--
--  Cubre TODOS los reportes: ventas detalladas, ventas por producto,
--  productos mas vendidos, ventas por categoria, ventas por metodo de pago,
--  pedidos por estado, pedidos por mesa, ocupacion de mesas, sesiones QR,
--  pedidos detallados, usuarios por rol, menu por categoria y resumen general.
-- =====================================================================

USE sistema;

-- ---------------------------------------------------------------------
-- 1) METODOS DE PAGO  (para "Reporte de Ventas por Metodo de Pago")
-- ---------------------------------------------------------------------
INSERT INTO Metodo_pago (id_pago, Tipo_pago) VALUES
(1, 'Efectivo'),
(2, 'Tarjeta'),
(3, 'Nequi'),
(4, 'Daviplata');

-- ---------------------------------------------------------------------
-- 2) SESIONES DE MESA (QR)  (para "Reporte de Sesiones de Clientes (QR)")
--    id_sesion explicito para poder enlazarlo desde Pedido.
-- ---------------------------------------------------------------------
INSERT INTO Sesion_Mesa (id_sesion, id_mesa, codigo_acceso, nombre_cliente, cedula_cliente, fecha_inicio, fecha_fin, activa) VALUES
(1, 1, 'A1B2C3', 'Andres Castro',   1010101010, '2025-01-05 12:30:00', '2025-01-05 13:45:00', 0),
(2, 2, 'D4E5F6', 'Laura Jimenez',   1020202020, '2025-01-12 19:10:00', '2025-01-12 20:05:00', 0),
(3, 3, 'G7H8I9', 'Pedro Nieto',     1030303030, '2025-02-03 13:00:00', '2025-02-03 14:20:00', 0),
(4, 1, 'J1K2L3', 'Sofia Vargas',    1040404040, '2025-02-15 20:00:00', '2025-02-15 21:10:00', 0),
(5, 4, 'M4N5O6', 'Diego Rojas',     1050505050, '2025-03-01 14:30:00', '2025-03-01 15:40:00', 0),
(6, 2, 'P7Q8R9', 'Camila Duarte',   1060606060, '2025-03-10 18:45:00', '2025-03-10 19:55:00', 0),
(7, 3, 'S1T2U3', 'Jorge Medina',    1070707070, '2025-03-20 12:15:00', NULL,                  1),
(8, 1, 'V4W5X6', 'Natalia Pinzon',  1080808080, '2025-03-25 13:50:00', NULL,                  1),
(9, 4, 'Y7Z8A9', 'Ricardo Peña',    1090909090, '2025-03-28 19:30:00', NULL,                  1),
(10,2, 'B1C2D3', 'Valentina Cruz',  1011121314, '2025-03-30 20:15:00', '2025-03-30 21:25:00', 0);

-- ---------------------------------------------------------------------
-- 3) PEDIDOS  (para "Pedidos por Estado", "Pedidos por Mesa", etc.)
--    id_pedido explicito. Estados variados y prioridades variadas.
--    Los pedidos 1-6 y 10 quedan 'entregado' (tendran factura).
--    Los pedidos 7,8,9 quedan en curso (sin factura).
-- ---------------------------------------------------------------------
INSERT INTO Pedido (id_pedido, id_mesa, mesero_tipo_doc, mesero_id_usuario, cliente_tipo_doc, cliente_id_usuario, id_sesion_qr, fecha_pedido, estado, prioridad, cocinero_asignado, tiempo_estimado, observaciones) VALUES
(1,  1, NULL, NULL, NULL, NULL, 1,  '2025-01-05 12:32:00', 'entregado',      'normal',  1053872530, 15, 'Sin cebolla en la hamburguesa'),
(2,  2, NULL, NULL, NULL, NULL, 2,  '2025-01-12 19:12:00', 'entregado',      'urgente', 1070919081, 20, 'Cliente con afan'),
(3,  3, NULL, NULL, NULL, NULL, 3,  '2025-02-03 13:05:00', 'entregado',      'normal',  1053872530, 15, 'Mesa familiar'),
(4,  1, NULL, NULL, NULL, NULL, 4,  '2025-02-15 20:02:00', 'entregado',      'normal',  1070919081, 15, NULL),
(5,  4, NULL, NULL, NULL, NULL, 5,  '2025-03-01 14:32:00', 'entregado',      'urgente', 1053872530, 25, 'Doble porcion de papas'),
(6,  2, NULL, NULL, NULL, NULL, 6,  '2025-03-10 18:47:00', 'entregado',      'normal',  1070919081, 15, NULL),
(7,  3, NULL, NULL, NULL, NULL, 7,  '2025-03-20 12:17:00', 'en_preparacion', 'normal',  1053872530, 15, 'Termino medio'),
(8,  1, NULL, NULL, NULL, NULL, 8,  '2025-03-25 13:52:00', 'pendiente',      'urgente', NULL,       15, 'Recien escaneado'),
(9,  4, NULL, NULL, NULL, NULL, 9,  '2025-03-28 19:32:00', 'en_camino',      'normal',  1070919081, 18, 'Va en camino a la mesa'),
(10, 2, NULL, NULL, NULL, NULL, 10, '2025-03-30 20:17:00', 'entregado',      'normal',  1053872530, 15, NULL);

-- ---------------------------------------------------------------------
-- 4) DETALLE DE PEDIDO  (para "Ventas por Producto", "Mas Vendidos",
--    "Ventas por Categoria", "Detallado de Pedidos")
--    SE INSERTA ANTES DE Factura para que el trigger calcule el Total.
--    valor_venta = precio del producto en Menu.
--    Menu: 1=14000, 2=16000, 3=13000, 4=10000
-- ---------------------------------------------------------------------
INSERT INTO Detalle_Pedido (id_pedido, id_menu, cantidad, valor_venta, observaciones) VALUES
-- Pedido 1  (total 38000)
(1, 1, 2, 14000, 'Sin cebolla'),
(1, 4, 1, 10000, NULL),
-- Pedido 2  (total 42000)
(2, 2, 1, 16000, NULL),
(2, 3, 2, 13000, 'Extra queso'),
-- Pedido 3  (total 62000)
(3, 1, 3, 14000, NULL),
(3, 4, 2, 10000, NULL),
-- Pedido 4  (total 23000)
(4, 3, 1, 13000, NULL),
(4, 4, 1, 10000, NULL),
-- Pedido 5  (total 32000)
(5, 2, 2, 16000, 'Doble porcion papas'),
-- Pedido 6  (total 43000)
(6, 1, 1, 14000, NULL),
(6, 2, 1, 16000, NULL),
(6, 3, 1, 13000, NULL),
-- Pedido 7  (en preparacion, total 14000)
(7, 1, 1, 14000, 'Termino medio'),
-- Pedido 8  (pendiente, total 26000)
(8, 2, 1, 16000, NULL),
(8, 4, 1, 10000, NULL),
-- Pedido 9  (en camino, total 26000)
(9, 3, 2, 13000, NULL),
-- Pedido 10 (total 30000)
(10, 4, 3, 10000, NULL);

-- ---------------------------------------------------------------------
-- 5) FACTURAS  (para "Ventas Detalladas" y todos los reportes de ventas)
--    Solo para pedidos entregados (1-6 y 10). id_factura explicito.
--    El Total lo calcula solo el trigger trg_total_factura; se pone 0.
-- ---------------------------------------------------------------------
INSERT INTO Factura (id_factura, id_pedido, Fecha_hora, Total) VALUES
(1, 1,  '2025-01-05 13:45:00', 0),
(2, 2,  '2025-01-12 20:05:00', 0),
(3, 3,  '2025-02-03 14:20:00', 0),
(4, 4,  '2025-02-15 21:10:00', 0),
(5, 5,  '2025-03-01 15:40:00', 0),
(6, 6,  '2025-03-10 19:55:00', 0),
(7, 10, '2025-03-30 21:25:00', 0);

-- ---------------------------------------------------------------------
-- 6) FACTURA x METODO DE PAGO  (para "Ventas por Metodo de Pago")
--    monto = total de cada factura (pago unico por factura).
-- ---------------------------------------------------------------------
INSERT INTO Factura_has_Metodo_pago (pkfk_n_factura, pkfk_metodo_pago, monto) VALUES
(1, 1, 38000),  -- Efectivo
(2, 2, 42000),  -- Tarjeta
(3, 3, 62000),  -- Nequi
(4, 1, 23000),  -- Efectivo
(5, 2, 32000),  -- Tarjeta
(6, 4, 43000),  -- Daviplata
(7, 3, 30000);  -- Nequi

-- ---------------------------------------------------------------------
-- 7) CORRECCION DE ESTADOS DE MESA  (para "Ocupacion de Mesas")
--    Los triggers dejaron todas las mesas ocupadas; ajustamos a la
--    realidad: solo quedan ocupadas las mesas con pedidos en curso.
--      Mesa 1 -> pedido 8 pendiente   => Ocupada (1)
--      Mesa 2 -> pedido 10 entregado  => Libre (0)
--      Mesa 3 -> pedido 7 en_preparacion => Ocupada (1)
--      Mesa 4 -> pedido 9 en_camino   => Ocupada (1)
-- ---------------------------------------------------------------------
UPDATE Mesa SET Estado = 1 WHERE id_Mesa IN (1, 3, 4);
UPDATE Mesa SET Estado = 0 WHERE id_Mesa = 2;

-- =====================================================================
--  FIN DE LOS DATOS DE EJEMPLO
-- =====================================================================
