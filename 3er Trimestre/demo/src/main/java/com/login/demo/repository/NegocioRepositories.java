package com.login.demo.repository;
import com.login.demo.model.entity.*; import org.springframework.data.jpa.repository.JpaRepository;
interface MesaRepository extends JpaRepository<Mesa,Integer> {}
interface MenuRepository extends JpaRepository<Menu,Integer> {}
interface PedidoRepository extends JpaRepository<Pedido,Integer> {}
interface FacturaRepository extends JpaRepository<Factura,Integer> {}
