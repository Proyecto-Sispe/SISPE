package com.sispe.springboot_web.Repository;

import com.sispe.springboot_web.Model.MenuInsumo;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface MenuInsumoRepository extends JpaRepository<MenuInsumo, Long> {

    List<MenuInsumo> findByMenu_Id(Integer menuId);
    Optional<MenuInsumo> findByMenu_IdAndInsumo_Id(Integer menuId, Long insumoId);
}