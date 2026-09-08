package com.sispe.springboot_web.config;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

class CompatiblePasswordEncoderTest {

    private final CompatiblePasswordEncoder encoder = new CompatiblePasswordEncoder();

    @Test
    void rejectsPlainTextPassword() {
        assertFalse(encoder.matches("1234", "1234"));
    }

    @Test
    void rejectsBlankEncodedPassword() {
        assertFalse(encoder.matches("1234", " "));
    }

    @Test
    void encodesAndMatchesBcryptPassword() {
        String encoded = encoder.encode("secreto");

        assertTrue(encoded.startsWith("$2"));
        assertTrue(encoder.matches("secreto", encoded));
        assertFalse(encoder.matches("incorrecta", encoded));
    }
}
