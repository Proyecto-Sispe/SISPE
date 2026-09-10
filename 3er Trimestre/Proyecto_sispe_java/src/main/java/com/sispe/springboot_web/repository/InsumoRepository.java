package com.sispe.springboot_web.repository;

import com.sispe.springboot_web.model.Insumo;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface InsumoRepository extends JpaRepository<Insumo, Long> {
    List<Insumo> findByActivoTrueOrderByNombreAsc();
}
