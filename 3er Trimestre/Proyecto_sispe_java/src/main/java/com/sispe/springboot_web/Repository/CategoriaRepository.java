package com.sispe.springboot_web.Repository;

import com.sispe.springboot_web.Model.Categoria;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CategoriaRepository extends JpaRepository<Categoria, Integer> {
}