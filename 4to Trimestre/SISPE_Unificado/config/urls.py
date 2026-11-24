from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from seguimiento_pedidos import views as acceso

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", acceso.home, name="home"),
    path("registro/", acceso.registro_view, name="registro"),
    path("portal/", TemplateView.as_view(template_name="portal/portal.html"), name="portal"),
    # Acceso unico (Sistema_sispe): personas SISPE por correo o usuarios de Django
    path("login/", acceso.login_view, name="login"),
    path("logout/", acceso.logout_view, name="logout"),
    path("", include("seguimiento_pedidos.urls")),
    # Carta digital (los QR antiguos /?mesa=N se redirigen desde home)
    path("", include("menu.urls")),
    path("", include("pedidos.urls")),
    path("cocina/", include("cocina.urls")),
    # Sistema_Victor
    path("servicio/", include("mesas_pedidos.urls")),
    # Modulo de administracion (usuarios, menu, inventario, facturas, pedidos)
    path("administracion/", include("administracion.urls")),
    # parte juan davisito
    path("estadisticas/", include("dashboard.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "SISPE · Administración"
admin.site.site_title = "SISPE"
admin.site.index_title = "Panel de administración"
