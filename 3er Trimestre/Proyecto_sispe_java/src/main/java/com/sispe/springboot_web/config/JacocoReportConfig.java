package com.sispe.springboot_web.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class JacocoReportConfig implements WebMvcConfigurer {

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        registry.addResourceHandler(
            "/index.html",
                "/jacoco-sessions.html",
                "/com.sispe.springboot_web.controller/**",
                "/com.sispe.springboot_web.model/**",
                "/com.sispe.springboot_web.service/**")
            .addResourceLocations("file:target/site/jacoco/");

        registry.addResourceHandler("/jacoco-resources/**")
            .addResourceLocations("file:target/site/jacoco/jacoco-resources/");
    }
}