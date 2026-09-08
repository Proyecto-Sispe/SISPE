package com.sispe.springboot_web.config;

import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.util.StringUtils;

/**
 * Permite autenticar temporalmente los registros existentes cuyo Password está
 * almacenado en texto plano en el script SQL, y usa BCrypt para las nuevas claves.
 * Recomendación: migrar las contraseñas existentes a BCrypt y eliminar el modo legacy.
 */
public class CompatiblePasswordEncoder implements PasswordEncoder {

    private final BCryptPasswordEncoder bcrypt = new BCryptPasswordEncoder();

    @Override
    public String encode(CharSequence rawPassword) {
        return bcrypt.encode(rawPassword);
    }

    @Override
    public boolean matches(CharSequence rawPassword, String encodedPassword) {
        if (!StringUtils.hasText(encodedPassword)) {
            return false;
        }

        if (encodedPassword.startsWith("$2a$") || encodedPassword.startsWith("$2b$") || encodedPassword.startsWith("$2y$")) {
            return bcrypt.matches(rawPassword, encodedPassword);
        }

        // Compatibilidad temporal con los usuarios iniciales del SQL (ej. 1234).
        return rawPassword != null && rawPassword.toString().equals(encodedPassword);
    }
}
