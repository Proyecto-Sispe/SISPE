package com.sispe.springboot_web.Repository;

import com.sispe.springboot_web.Model.Insumo;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface InsumoRepository extends JpaRepository<Insumo, Long> {
    List<Insumo> findByActivoTrueOrderByNombreAsc();
}
