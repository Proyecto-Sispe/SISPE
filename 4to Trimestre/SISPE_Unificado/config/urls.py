from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import TemplateView

from seguimiento_pedidos import views as acceso

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", acceso.home, name="home"),
    path("registro/", acceso.registro_view, name="registro"),
    path("portal/", TemplateView.as_view(template_name="portal/portal.html"), name="portal"),
    # Acceso único: personas SISPE por correo o usuarios de Django.
    path("login/", acceso.login_view, name="login"),
    path("logout/", acceso.logout_view, name="logout"),
    path("", include("seguimiento_pedidos.urls")),
    # Carta digital (los QR antiguos /?mesa=N se redirigen desde home)
    path("", include("menu.urls")),
    path("", include("pedidos.urls")),
    path("cocina/", include("cocina.urls")),
    # Mesas y pedidos en sala
    path("servicio/", include("mesas_pedidos.urls")),
    # Modulo de administracion (usuarios, menu, inventario, facturas, pedidos)
    path("administracion/", include("administracion.urls")),
    # Compatibilidad: las estadísticas ahora están dentro de reportes.
    path("estadisticas/", include("dashboard.urls")),

    # --------------------------------------------------------------------
    # RECUPERACIÓN DE CONTRASEÑA
    # --------------------------------------------------------------------
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Centro de Gestión SISPE"
admin.site.site_title = "SISPE | Gestión"
admin.site.index_title = "Bienvenido al Centro de Gestión"
