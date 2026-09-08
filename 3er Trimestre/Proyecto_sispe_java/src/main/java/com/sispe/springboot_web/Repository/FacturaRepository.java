package com.sispe.springboot_web.Repository;

import com.sispe.springboot_web.Model.Factura;
import org.springframework.data.jpa.repository.JpaRepository;

public interface FacturaRepository extends JpaRepository<Factura, Long> {}