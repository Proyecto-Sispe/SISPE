package com.sispe.springboot_web.Service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.Optional;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.sispe.springboot_web.Model.Pedido;
import com.sispe.springboot_web.Repository.PedidoRepository;

@ExtendWith(MockitoExtension.class)
class PedidoServiceTest {

    @Mock
    private PedidoRepository repository;

    @Mock
    private SesionMesaService sesionMesaService;

    @Mock
    private InventarioService inventarioService;

    private PedidoService pedidoService;

    @BeforeEach
    void setUp() {
        pedidoService = new PedidoService(repository, sesionMesaService, inventarioService);
    }

    private Pedido pedido(String estado) {
        return Pedido.builder().id(1L).mesaId(4L).estado(estado).prioridad("urgente").build();
    }

    @Test
    void rechazaUnEstadoQueNoExiste() {
        IllegalArgumentException error = assertThrows(IllegalArgumentException.class,
                () -> pedidoService.cambiarEstado(1L, "cancelado"));

        assertEquals("Estado de pedido no válido", error.getMessage());
        verify(repository, never()).findById(any());
    }

    @Test
    void rechazaUnPedidoQueNoExiste() {
        when(repository.findById(1L)).thenReturn(Optional.empty());

        IllegalArgumentException error = assertThrows(IllegalArgumentException.class,
                () -> pedidoService.cambiarEstado(1L, "en_preparacion"));

        assertEquals("El pedido #1 no existe", error.getMessage());
    }

    @Test
    void pasarAEnPreparacionNoDescuentaInventarioNiDespacha() {
        Pedido pedido = pedido("pendiente");
        when(repository.findById(1L)).thenReturn(Optional.of(pedido));
        when(repository.save(pedido)).thenReturn(pedido);

        Pedido resultado = pedidoService.cambiarEstado(1L, "en_preparacion");

        assertEquals("en_preparacion", resultado.getEstado());
        verify(inventarioService, never()).descontarPedido(any());
        verify(sesionMesaService, never()).despacharPedido(any());
    }

    @Test
    void pasarAEnCaminoBajaLaPrioridadAUrgenteParaQueNoSigaResaltadoEnCocina() {
        Pedido pedido = pedido("en_preparacion");
        when(repository.findById(1L)).thenReturn(Optional.of(pedido));
        when(repository.save(pedido)).thenReturn(pedido);

        pedidoService.cambiarEstado(1L, "en_camino");

        assertEquals("normal", pedido.getPrioridad());
    }

    @Test
    void entregarDescuentaInventarioYDespachaUnaSolaVez() {
        Pedido pedido = pedido("en_camino");
        when(repository.findById(1L)).thenReturn(Optional.of(pedido));
        when(repository.save(pedido)).thenReturn(pedido);

        Pedido resultado = pedidoService.entregarYDescontarStock(1L);

        assertEquals("entregado", resultado.getEstado());
        verify(inventarioService, times(1)).descontarPedido(1L);
        verify(sesionMesaService, times(1)).despacharPedido(1L);
    }

    @Test
    void siNoHayStockElPedidoNoCambiaDeEstadoNiSeDespacha() {
        Pedido pedido = pedido("en_camino");
        when(repository.findById(1L)).thenReturn(Optional.of(pedido));
        doThrow(new IllegalStateException("Stock insuficiente para: Queso"))
                .when(inventarioService).descontarPedido(1L);

        assertThrows(IllegalStateException.class, () -> pedidoService.entregarYDescontarStock(1L));

        assertEquals("en_camino", pedido.getEstado(), "el estado no debe cambiar si falta stock");
        verify(repository, never()).save(any());
        verify(sesionMesaService, never()).despacharPedido(any());
    }

    @Test
    void volverAMarcarEntregadoUnPedidoYaEntregadoNoDuplicaElDescuento() {
        Pedido pedido = pedido("entregado");
        when(repository.findById(1L)).thenReturn(Optional.of(pedido));
        when(repository.save(pedido)).thenReturn(pedido);

        pedidoService.cambiarEstado(1L, "entregado");

        verify(inventarioService, never()).descontarPedido(any());
        verify(sesionMesaService, never()).despacharPedido(any());
    }

    @Test
    void unPedidoEntregadoNoPuedeRetroceder() {
        Pedido pedido = pedido("entregado");
        when(repository.findById(1L)).thenReturn(Optional.of(pedido));

        IllegalStateException error = assertThrows(IllegalStateException.class,
                () -> pedidoService.cambiarEstado(1L, "pendiente"));

        assertEquals("Un pedido entregado no puede retroceder", error.getMessage());
        verify(repository, never()).save(any());
    }
}
