package com.sispe.springboot_web.Controller;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.Optional;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import com.sispe.springboot_web.Model.Pedido;
import com.sispe.springboot_web.Repository.FacturaRepository;
import com.sispe.springboot_web.Repository.MesaRepository;
import com.sispe.springboot_web.Repository.PedidoRepository;
import com.sispe.springboot_web.Service.PedidoService;

@ExtendWith(MockitoExtension.class)
class PedidoControllerTest {

    @Mock
    private PedidoRepository pedidos;
    @Mock
    private PedidoService pedidoService;
    @Mock
    private FacturaRepository facturas;
    @Mock
    private MesaRepository mesas;
    @Mock
    private Model model;
    @Mock
    private RedirectAttributes attrs;
    @Mock
    private BindingResult binding;

    private PedidoController controller;

    @BeforeEach
    void setUp() {
        controller = new PedidoController(pedidos, pedidoService, facturas, mesas);
    }

    @Test
    void guardarRechazaMesaSinNumero() {
        Pedido pedido = Pedido.builder().mesaId(null).build();

        String vista = controller.guardar(pedido, binding, model, attrs);

        assertEquals("pedidos/nuevo", vista);
        verify(model).addAttribute("error", "Indica un número de mesa válido (mayor que cero).");
        verify(pedidos, never()).save(any());
    }

    @Test
    void guardarRechazaMesaQueNoExiste() {
        Pedido pedido = Pedido.builder().mesaId(9L).build();
        when(mesas.existsById(9)).thenReturn(false);

        controller.guardar(pedido, binding, model, attrs);

        verify(model).addAttribute("error", "La mesa 9 no existe. Créala primero en el módulo Mesas.");
        verify(pedidos, never()).save(any());
    }

    @Test
    void guardarRechazaPrioridadQueNoCoincideConElEnumDeLaBaseDeDatos() {
        Pedido pedido = Pedido.builder().mesaId(1L).prioridad("alta").build();
        when(mesas.existsById(1)).thenReturn(true);

        controller.guardar(pedido, binding, model, attrs);

        verify(model).addAttribute("error", "La prioridad seleccionada no es válida.");
        verify(pedidos, never()).save(any());
    }

    @Test
    void guardarValidoAsignaPendienteYNormalPorDefecto() {
        Pedido pedido = Pedido.builder().mesaId(1L).build();
        when(mesas.existsById(1)).thenReturn(true);
        when(pedidos.save(pedido)).thenReturn(Pedido.builder().id(10L).build());

        String vista = controller.guardar(pedido, binding, model, attrs);

        assertEquals("redirect:/pedidos", vista);
        assertEquals("pendiente", pedido.getEstado());
        assertEquals("normal", pedido.getPrioridad());
        assertNull(pedido.getId(), "el endpoint /guardar solo crea, nunca debe conservar un id recibido");
        verify(attrs).addFlashAttribute("ok", "Pedido #10 registrado correctamente.");
    }

    @Test
    void guardarMuestraMensajeAmigableSiFallaLaBaseDeDatos() {
        Pedido pedido = Pedido.builder().mesaId(1L).build();
        when(mesas.existsById(1)).thenReturn(true);
        when(pedidos.save(pedido)).thenThrow(new DataIntegrityViolationException("fk violada"));

        String vista = controller.guardar(pedido, binding, model, attrs);

        assertEquals("pedidos/nuevo", vista);
        verify(model).addAttribute("error", "No se pudo guardar el pedido. Verifica los datos e inténtalo de nuevo.");
    }

    @Test
    void actualizarInformaCuandoElPedidoNoExiste() {
        when(pedidos.findById(5L)).thenReturn(Optional.empty());

        String vista = controller.actualizar(5L, new Pedido(), binding, model, attrs);

        assertEquals("redirect:/pedidos", vista);
        verify(attrs).addFlashAttribute("error", "El pedido #5 no existe.");
    }

    @Test
    void actualizarCambiaEstadoAtravesDelServicioSoloSiCambio() {
        Pedido existente = Pedido.builder().id(5L).mesaId(1L).estado("pendiente").build();
        Pedido formulario = Pedido.builder().mesaId(1L).estado("en_preparacion").prioridad("normal").build();
        when(pedidos.findById(5L)).thenReturn(Optional.of(existente), Optional.of(existente));
        when(mesas.existsById(1)).thenReturn(true);

        String vista = controller.actualizar(5L, formulario, binding, model, attrs);

        assertEquals("redirect:/pedidos", vista);
        verify(pedidoService).cambiarEstado(5L, "en_preparacion");
        verify(pedidos).save(existente);
        verify(attrs).addFlashAttribute("ok", "Pedido #5 actualizado correctamente.");
    }

    @Test
    void actualizarNoLlamaAlServicioSiElEstadoNoCambio() {
        Pedido existente = Pedido.builder().id(5L).mesaId(1L).estado("pendiente").build();
        Pedido formulario = Pedido.builder().mesaId(1L).estado("pendiente").build();
        when(pedidos.findById(5L)).thenReturn(Optional.of(existente), Optional.of(existente));
        when(mesas.existsById(1)).thenReturn(true);

        controller.actualizar(5L, formulario, binding, model, attrs);

        verify(pedidoService, never()).cambiarEstado(any(), any());
    }

    @Test
    void actualizarMuestraElErrorDeUnaTransicionInvalida() {
        Pedido existente = Pedido.builder().id(5L).mesaId(1L).estado("entregado").build();
        Pedido formulario = Pedido.builder().mesaId(1L).estado("pendiente").build();
        when(pedidos.findById(5L)).thenReturn(Optional.of(existente));
        when(mesas.existsById(1)).thenReturn(true);
        org.mockito.Mockito.doThrow(new IllegalStateException("Un pedido entregado no puede retroceder"))
                .when(pedidoService).cambiarEstado(5L, "pendiente");

        String vista = controller.actualizar(5L, formulario, binding, model, attrs);

        assertEquals("pedidos/nuevo", vista);
        verify(model).addAttribute("error", "Un pedido entregado no puede retroceder");
        verify(pedidos, never()).save(any());
    }

    @Test
    void eliminarInformaCuandoElPedidoTieneRegistrosAsociados() {
        org.mockito.Mockito.doThrow(new DataIntegrityViolationException("fk"))
                .when(pedidos).deleteById(3L);

        String vista = controller.eliminar(3L, attrs);

        assertEquals("redirect:/pedidos", vista);
        verify(attrs).addFlashAttribute("error",
                "No se puede eliminar el pedido #3 porque tiene registros asociados (por ejemplo pagos o notificaciones).");
    }

    @Test
    void marcarEntregadoDelegaEnElServicioYMuestraConfirmacion() {
        String vista = controller.marcarEntregado(7L, attrs);

        assertEquals("redirect:/pedidos/entregar", vista);
        verify(pedidoService).entregarYDescontarStock(7L);
        verify(attrs).addFlashAttribute("ok", "Pedido #7 entregado. Stock descontado.");
    }

    @Test
    void marcarEntregadoMuestraElErrorSiNoHayStock() {
        org.mockito.Mockito.doThrow(new IllegalStateException("Stock insuficiente para: Queso"))
                .when(pedidoService).entregarYDescontarStock(7L);

        controller.marcarEntregado(7L, attrs);

        verify(attrs).addFlashAttribute("error", "Stock insuficiente para: Queso");
    }
}
