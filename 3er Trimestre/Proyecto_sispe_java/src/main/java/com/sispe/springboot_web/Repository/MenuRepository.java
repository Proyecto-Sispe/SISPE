package com.sispe.springboot_web.Repository;

import com.sispe.springboot_web.Model.Menu;
import org.springframework.data.jpa.repository.JpaRepository;

public interface MenuRepository extends JpaRepository<Menu, Integer> {}