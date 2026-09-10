package com.sispe.springboot_web.repository;

import com.sispe.springboot_web.model.Factura;
import org.springframework.data.jpa.repository.JpaRepository;

public interface FacturaRepository extends JpaRepository<Factura, Long> {}