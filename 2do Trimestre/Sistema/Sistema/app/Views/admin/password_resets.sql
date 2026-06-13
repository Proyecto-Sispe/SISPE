-- ============================================================
-- Tabla para la recuperacion de contrasena (SISPE API)
-- Ejecutar en la base de datos `sistema`.
-- ============================================================

CREATE TABLE IF NOT EXISTS `password_resets` (
  `id`         INT(11)      NOT NULL AUTO_INCREMENT,
  `correo`     VARCHAR(120) NOT NULL,
  `token`      VARCHAR(64)  NOT NULL,   -- hash sha256 del token enviado por correo
  `codigo`     VARCHAR(6)   NOT NULL,   -- codigo de 6 digitos enviado por correo
  `expira`     DATETIME     NOT NULL,   -- fecha/hora de expiracion (15 min)
  `usado`      TINYINT(1)   NOT NULL DEFAULT 0,
  `created_at` DATETIME     NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_correo` (`correo`),
  KEY `idx_token`  (`token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
