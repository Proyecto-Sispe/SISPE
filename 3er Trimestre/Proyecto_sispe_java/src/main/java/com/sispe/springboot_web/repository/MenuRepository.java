package com.sispe.springboot_web.repository;

import com.sispe.springboot_web.model.Menu;
import org.springframework.data.jpa.repository.JpaRepository;

public interface MenuRepository extends JpaRepository<Menu, Integer> {}