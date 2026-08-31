package com.sispe.springboot_web.Repository;

import org.springframework.data.jpa.repository.JpaRepository;

import com.sispe.springboot_web.Model.Rol;

public interface RolRepository extends JpaRepository<Rol, Integer> {
}