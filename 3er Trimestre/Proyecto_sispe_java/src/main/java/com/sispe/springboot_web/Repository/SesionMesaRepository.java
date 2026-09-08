package com.sispe.springboot_web.Repository;

import com.sispe.springboot_web.Model.SesionMesa;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface SesionMesaRepository extends JpaRepository<SesionMesa, Long> {
    Optional<SesionMesa> findByMesaIdAndActivaTrue(Integer mesaId);
}