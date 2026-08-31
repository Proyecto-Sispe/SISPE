package com.sispe.springboot_web.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
public class SecurityConfig {

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new CompatiblePasswordEncoder();
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {

        http
            // Control de acceso a URLs según Rol
            .authorizeHttpRequests(auth -> auth
                // Rutas públicas
              .requestMatchers(
    "/login",
    "/login/olvide",
    "/login/verificar",
    "/registro",
    "/css/**",
    "/js/**",
    "/images/**",
    "/menu/digital"
).permitAll()

.requestMatchers("/admin/**").hasRole("ADMINISTRADOR")
.requestMatchers("/menu/**", "/api/menu/**").hasRole("ADMINISTRADOR")
.requestMatchers("/cocina/**").hasAnyRole("ADMINISTRADOR", "COCINERO")
.requestMatchers("/pedidos/**").hasAnyRole("ADMINISTRADOR", "MESERO")
.requestMatchers("/cliente/**").hasRole("CLIENTE")
                // Cualquier otra ruta requiere estar autenticado
                .anyRequest().authenticated()
            )

            // Configuración del formulario de Login
            .formLogin(form -> form
                .loginPage("/login")
                .loginProcessingUrl("/login")
                .defaultSuccessUrl("/inicio", true)
                .permitAll()
            )

            // Configuración de Logout
            .logout(logout -> logout
                .logoutUrl("/logout")
                .logoutSuccessUrl("/login?logout")
                .permitAll()
            )

            // Si el usuario está autenticado pero no tiene el rol requerido
            // para un módulo, se muestra una página de acceso denegado.
            .exceptionHandling(exception -> exception
                .accessDeniedPage("/acceso-denegado")
            );

        return http.build();
    }
}