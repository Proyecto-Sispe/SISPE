package com.login.demo.model.entity;

import java.io.Serializable;
import jakarta.persistence.Embeddable;
import lombok.*;

@Embeddable @Getter @Setter @NoArgsConstructor @AllArgsConstructor @EqualsAndHashCode
public class PersonaId implements Serializable { private Integer idUsuario; private Integer tipoDoc; }
