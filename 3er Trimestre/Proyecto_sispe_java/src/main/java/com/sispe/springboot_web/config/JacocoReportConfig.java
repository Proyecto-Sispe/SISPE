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
                "/com.sispe.springboot_web.Controller/**",
                "/com.sispe.springboot_web.Model/**",
                "/com.sispe.springboot_web.Service/**")
            .addResourceLocations("file:target/site/jacoco/");

        registry.addResourceHandler("/jacoco-resources/**")
            .addResourceLocations("file:target/site/jacoco/jacoco-resources/");
    }
}