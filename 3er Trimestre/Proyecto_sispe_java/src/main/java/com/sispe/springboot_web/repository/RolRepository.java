package com.sispe.springboot_web.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import com.sispe.springboot_web.model.Rol;

public interface RolRepository extends JpaRepository<Rol, Integer> {
}