package com.sispe.springboot_web;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;

/**
 * Punto de entrada de la aplicación web SISPE.
 *
 * <p>La clase habilita el autoconfigurado de Spring Boot y la seguridad a
 * nivel de método para proteger las operaciones de negocio.</p>
 */
@SpringBootApplication
@EnableMethodSecurity
public class SpringbootWebApplication {

	/**
	 * Inicia el contexto de Spring y el servidor embebido.
	 *
	 * @param args argumentos recibidos desde la línea de comandos
	 */
	public static void main(String[] args) {
		SpringApplication.run(SpringbootWebApplication.class, args);
	}

}
