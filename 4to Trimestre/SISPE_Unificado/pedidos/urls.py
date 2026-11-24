from django.urls import path

from . import views

urlpatterns = [
    path("carrito/", views.ver, name="carrito"),
    path("carrito/agregar/", views.agregar, name="carrito_agregar"),
    path("carrito/linea/<str:clave>/", views.actualizar, name="carrito_actualizar"),
    path("carrito/quitar/<str:clave>/", views.quitar, name="carrito_quitar"),
    path("carrito/vaciar/", views.vaciar, name="carrito_vaciar"),
    path("confirmar/", views.confirmar, name="confirmar"),
    path("seguimiento/<int:pk>/", views.seguimiento, name="seguimiento"),
    path("seguimiento/<int:pk>/estado.json", views.estado_json, name="seguimiento_json"),
    # Flujo del cliente: Cancelación, Despedida, Finalización, Factura y Pago PSE
    path("pedido/<int:pk>/cancelar/", views.cancelar_pedido, name="cancelar_pedido"),
    path("despedida/", views.despedida_cliente, name="despedida_cliente"),
    path("pedido/<int:pk>/finalizar/", views.finalizar_pedido, name="finalizar_pedido"),
    path("pedido/<int:pk>/factura/", views.factura_cliente, name="factura_cliente"),
    path("pedido/<int:pk>/pagar-pse/", views.pagar_pse, name="pagar_pse"),
    path("pedido/<int:pk>/comprobante/", views.comprobante_pago, name="comprobante_pago"),
]
