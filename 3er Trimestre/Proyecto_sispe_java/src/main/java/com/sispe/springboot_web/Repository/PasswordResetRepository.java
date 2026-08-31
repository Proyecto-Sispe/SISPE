package com.sispe.springboot_web.Repository;

import com.sispe.springboot_web.Model.PasswordReset;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface PasswordResetRepository extends JpaRepository<PasswordReset, Long> {
    Optional<PasswordReset> findFirstByCorreoAndUsadoFalseOrderByCreatedAtDesc(String correo);
}