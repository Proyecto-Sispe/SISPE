package com.login.demo.model.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity @Table(name="Menu") @Getter @Setter @NoArgsConstructor
public class Menu { @Id @Column(name="id_menu") private Integer id; @Column(name="Productos") private String producto; @Column(name="Precio") private Double precio; private String descripcion; @Column(name="pkfk_id_categoria") private Integer categoriaId; }
