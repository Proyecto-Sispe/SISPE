package com.sispe.springboot_web.Repository;

import com.sispe.springboot_web.Model.MenuInsumo;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface MenuInsumoRepository extends JpaRepository<MenuInsumo, Long> {
    List<MenuInsumo> findByMenuId(Integer menuId);
}
