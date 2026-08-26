package com.login.demo.model;

import java.io.Serializable;
import lombok.*;

@Getter @Setter @NoArgsConstructor @AllArgsConstructor @EqualsAndHashCode
public class UsuarioId implements Serializable {
    private Long id;
    private Integer tipoDocumento;
}
