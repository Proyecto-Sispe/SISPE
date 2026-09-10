package com.sispe.springboot_web.model;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;

import java.math.BigDecimal;

import org.junit.jupiter.api.Test;

class ModelTest {

    @Test
    void personaMantieneSusDatosYRoles() {
        Persona persona = new Persona();
        persona.setIdUsuario(10);
        persona.setTipoDocumento(1);
        persona.setPrimerNombre("Ana");
        persona.setSegundoNombre("Maria");
        persona.setPrimerApellido("Soto");
        persona.setSegundoApellido("Diaz");
        persona.setTelefono(3001234567L);
        persona.setCorreo("ana@test.com");
        persona.setPassword("hash");
        persona.setEstado(1);
        Rol rol = new Rol();
        rol.setIdRol(4);
        persona.getRoles().add(rol);

        assertEquals(10, persona.getIdUsuario());
        assertEquals(1, persona.getTipoDocumento());
        assertEquals("Ana", persona.getPrimerNombre());
        assertEquals("Maria", persona.getSegundoNombre());
        assertEquals("Soto", persona.getPrimerApellido());
        assertEquals("Diaz", persona.getSegundoApellido());
        assertEquals(3001234567L, persona.getTelefono());
        assertEquals("ana@test.com", persona.getCorreo());
        assertEquals("hash", persona.getPassword());
        assertEquals(1, persona.getEstado());
        assertEquals(1, persona.getRoles().size());
    }

    @Test
    void entidadesLombokMantienenValores() {
        Categoria categoria = new Categoria(2, "Bebidas");
        Menu menu = new Menu(3, "Cafe", BigDecimal.valueOf(5000), "Caliente", categoria);
        PasswordReset reset = new PasswordReset();
        reset.setCorreo("ana@test.com");
        reset.setToken("token");
        reset.setCodigo("123456");
        reset.setUsado(false);
        Rol rol = new Rol();
        rol.setIdRol(4);
        rol.setNombre("Cliente");

        assertEquals("Bebidas", categoria.getNombre());
        assertEquals("Cafe", menu.getProducto());
        assertEquals(BigDecimal.valueOf(5000), menu.getPrecio());
        assertEquals("Caliente", menu.getDescripcion());
        assertEquals(categoria, menu.getCategoria());
        assertEquals("token", reset.getToken());
        assertEquals("123456", reset.getCodigo());
        assertEquals(false, reset.getUsado());
        assertEquals("Cliente", rol.getNombre());
    }

    @Test
    void personaIdComparaSusDosComponentes() {
        PersonaId primero = new PersonaId(7, 1);
        PersonaId igual = new PersonaId(7, 1);
        PersonaId diferente = new PersonaId(7, 2);

        assertEquals(primero, igual);
        assertEquals(primero.hashCode(), igual.hashCode());
        assertNotEquals(primero, diferente);
        assertNotEquals(primero, null);
    }
}
