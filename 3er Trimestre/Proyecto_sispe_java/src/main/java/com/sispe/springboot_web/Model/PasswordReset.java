package com.sispe.springboot_web.Model;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "password_resets")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class PasswordReset {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) private Long id;
    @Column(nullable = false) private String correo;
    @Column(nullable = false, unique = true) private String token;
    private String codigo;
    private LocalDateTime expira;
    private Boolean usado = false;
    @Column(name = "created_at") private LocalDateTime createdAt;
}