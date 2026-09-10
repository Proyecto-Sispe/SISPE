package com.sispe.springboot_web.repository;

import com.sispe.springboot_web.model.Categoria;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CategoriaRepository extends JpaRepository<Categoria, Integer> {
}