package com.sispe.springboot_web.Repository;
import com.sispe.springboot_web.Model.Adicion;
import org.springframework.data.jpa.repository.JpaRepository;
public interface AdicionRepository extends JpaRepository<Adicion, Long> {}