import hashlib
import hmac
import json
import logging
import os
import secrets
import smtplib
from datetime import timedelta
from types import SimpleNamespace

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.hashers import (
    check_password,
    identify_hasher,
    make_password,
)
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from administracion.models import LoginThrottle
from administracion.permisos import DJANGO_DASHBOARD_GROUP, admin_required, rol_required

from .models import PasswordResets, Persona, PersonaHasRol, Rol, TipoDoc

logger = logging.getLogger(__name__)
RESET_EXPIRY = timedelta(minutes=15)
RESET_MAX_ATTEMPTS = 5
RESET_REQUEST_COOLDOWN = timedelta(minutes=1)
LOGIN_WINDOW = timedelta(minutes=15)
LOGIN_BUCKET_LIMITS = (8, 20)
RESET_GENERIC_RESPONSE = (
    "Si existe una cuenta activa con ese correo, recibirás instrucciones "
    "para restablecer la contraseña."
)


def _login_buckets(request, identifier):
    ip_address = request.META.get("REMOTE_ADDR", "unknown")
    values = (
        ("account-ip", f"{identifier.casefold()}|{ip_address}", LOGIN_BUCKET_LIMITS[0]),
        ("ip", ip_address, LOGIN_BUCKET_LIMITS[1]),
    )
    return [
        (
            hmac.new(
                settings.SECRET_KEY.encode("utf-8"),
                f"{scope}:{value}".encode("utf-8"),
                hashlib.sha256,
            ).hexdigest(),
            limit,
        )
        for scope, value, limit in values
    ]


def _login_is_limited(buckets, now):
    for key, limit in buckets:
        attempt = LoginThrottle.objects.using("default").filter(pk=key).first()
        if (
            attempt
            and attempt.attempts >= limit
            and attempt.blocked_until
            and attempt.blocked_until > now
        ):
            return True
    return False


def _record_login_failure(buckets, now):
    with transaction.atomic(using="default"):
        attempts = LoginThrottle.objects.using("default")
        attempts.filter(window_started__lt=now - timedelta(days=1)).delete()
        for key, limit in buckets:
            attempt, _ = attempts.select_for_update().get_or_create(
                pk=key,
                defaults={"window_started": now},
            )
            if attempt.window_started <= now - LOGIN_WINDOW:
                attempt.attempts = 0
                attempt.window_started = now
                attempt.blocked_until = None
            attempt.attempts += 1
            if attempt.attempts >= limit:
                attempt.blocked_until = now + LOGIN_WINDOW
            attempt.save(
                using="default",
                update_fields=["attempts", "window_started", "blocked_until"],
            )


def _clear_login_failures(buckets):
    LoginThrottle.objects.using("default").filter(
        pk__in=[key for key, _limit in buckets]
    ).delete()


def _verificar_password(password_ingresada, password_bd, persona=None):
    if not password_bd:
        return False
    try:
        identify_hasher(password_bd)
    except ValueError:
        if not hmac.compare_digest(password_ingresada, password_bd):
            return False
        if persona is not None:
            persona.password = make_password(password_ingresada)
            persona.save(using="sistema", update_fields=["password"])
        return True

    def actualizar_hash(password):
        persona.password = make_password(password)
        persona.save(using="sistema", update_fields=["password"])

    return check_password(
        password_ingresada,
        password_bd,
        setter=actualizar_hash if persona is not None else None,
    )


def _obtener_rol_usuario(persona):
    relacion = (
        PersonaHasRol.objects.select_related('pkfk_idrol')
        .filter(
            pkfk_id_usuario=persona.id_usuario,
            pkfk_tipo_doc=persona.pkfk_tipo_doc_id,
        )
        .first()
    )
    if relacion and relacion.pkfk_idrol:
        return relacion.pkfk_idrol.nom_rol.lower()
    return None


RUTAS_POR_ROL = {
    'administrador': 'dashboard_admin',
    'cocinero': 'dashboard_cocinero',
    'cajero': 'dashboard_cajero',
    'mesero': 'dashboard_mesero',
    'cliente': 'dashboard_cliente',
}

# Rol SISPE -> grupo de Django que usan las otras partes (p. ej. cocina pide "Chef")
GRUPO_POR_ROL = {
    'administrador': 'Administrador',
    'cocinero': 'Chef',
    'cajero': 'Cajero',
    'mesero': 'Mesero',
    'cliente': 'Cliente',
}


def _usuario_django(persona, rol, password=None):
    """Crea o actualiza el usuario de Django que acompana a la persona SISPE."""
    User = get_user_model()
    usuario, creado = User.objects.get_or_create(username=persona.correo_usu.lower())
    if password:
        usuario.set_password(password)
    elif creado:
        usuario.set_unusable_password()
    usuario.first_name = persona.nom1_usu or ''
    usuario.last_name = persona.ape1_usu or ''
    usuario.email = persona.correo_usu
    usuario.is_staff = rol == 'administrador'
    usuario.is_superuser = rol == 'administrador'
    usuario.save()
    grupo, _ = Group.objects.get_or_create(name=GRUPO_POR_ROL.get(rol, rol.title()))
    usuario.groups.set([grupo])
    return usuario


def _siguiente(request):
    destino = request.POST.get('next') or request.GET.get('next') or ''
    if destino and url_has_allowed_host_and_scheme(
        destino, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return destino
    return ''


def _pantalla_login(request):
    return render(request, 'seguimiento_pedidos/login.html', {'next': _siguiente(request)})


def login_view(request):
    """Acceso unico: personas SISPE (correo) o usuarios de Django (admin, chef)."""
    if request.method == 'POST':
        identificador = request.POST.get('correo', '').strip()
        password = request.POST.get('password', '')
        siguiente = _siguiente(request)
        buckets = _login_buckets(request, identificador)
        now = timezone.now()
        if _login_is_limited(buckets, now):
            messages.error(request, 'Correo/usuario o contrasena incorrectos.')
            return _pantalla_login(request)

        persona = Persona.objects.filter(
            correo_usu__iexact=identificador,
            estado=1,
        ).first()

        if persona and _verificar_password(password, persona.password, persona):
            rol = _obtener_rol_usuario(persona)
            if not rol or rol not in RUTAS_POR_ROL:
                messages.error(request, 'El usuario no tiene un rol valido asignado.')
                return _pantalla_login(request)

            _clear_login_failures(buckets)
            auth_login(request, _usuario_django(persona, rol, password))
            request.session['usuario_id'] = persona.id_usuario
            request.session['usuario_tipo_doc'] = persona.pkfk_tipo_doc_id
            request.session['usuario_nombre'] = f'{persona.nom1_usu} {persona.ape1_usu}'
            request.session['usuario_rol'] = rol
            return redirect(siguiente or RUTAS_POR_ROL[rol])

        usuario = authenticate(request, username=identificador, password=password)
        if usuario is not None:
            _clear_login_failures(buckets)
            auth_login(request, usuario)
            request.session['usuario_nombre'] = usuario.get_full_name() or usuario.username
            if usuario.groups.filter(name=DJANGO_DASHBOARD_GROUP).exists():
                request.session['usuario_rol'] = 'admin_django'
                return redirect('admin:index')
            request.session['usuario_rol'] = (
                'administrador' if (usuario.is_superuser or usuario.groups.filter(name='Administrador').exists())
                else 'cocinero' if usuario.groups.filter(name__in=['Chef', 'Cocinero']).exists()
                else 'cajero' if usuario.groups.filter(name__in=['Cajero', 'Caja']).exists()
                else 'mesero' if usuario.groups.filter(name__in=['Mesero', 'Meseros']).exists()
                else 'cliente'
            )
            return redirect(siguiente or RUTAS_POR_ROL.get(request.session['usuario_rol'], 'portal'))

        _record_login_failure(buckets, now)
        messages.error(request, 'Correo/usuario o contrasena incorrectos.')
        return _pantalla_login(request)

    return _pantalla_login(request)


def logout_view(request):
    auth_logout(request)
    return redirect('home')


@login_required
def cambiar_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        password_nueva = form.cleaned_data["new_password1"]
        persona_id = request.session.get("usuario_id")
        tipo_doc_id = request.session.get("usuario_tipo_doc")
        if persona_id and tipo_doc_id:
            persona = Persona.objects.using("sistema").filter(
                id_usuario=persona_id,
                pkfk_tipo_doc_id=tipo_doc_id,
            ).first()
            if persona:
                persona.password = make_password(password_nueva)
                persona.save(using="sistema", update_fields=["password"])

        usuario = form.save()
        update_session_auth_hash(request, usuario)
        messages.success(request, "La contraseña se actualizó correctamente.")
        return redirect("portal")

    return render(
        request,
        "seguimiento_pedidos/cambiar_password.html",
        {"form": form},
    )


def home(request):
    """Portada pública. Si llega un QR antiguo /?mesa=N, redirige a la carta."""
    mesa = (request.GET.get('mesa') or '').strip()
    if mesa:
        return redirect(f"{reverse('carta')}?mesa={mesa}")
    return render(request, 'inicio.html')


def _rol_cliente():
    return (
        Rol.objects.filter(nom_rol__iexact='cliente').first()
        or Rol.objects.filter(nom_rol__icontains='client').first()
    )


def registro_view(request):
    """Alta pública de clientes, equivalente a la vista PHP de registro."""
    if request.user.is_authenticated:
        return redirect('portal')

    tipos_doc = list(TipoDoc.objects.filter(estado=1).order_by('id_doc'))
    contexto = {'tipos_doc': tipos_doc}

    if request.method != 'POST':
        return render(request, 'registro.html', contexto)

    tipo_doc = (request.POST.get('doc') or '').strip()
    numero = (request.POST.get('id') or '').strip()
    nom1 = (request.POST.get('nombre1') or '').strip()
    nom2 = (request.POST.get('nombre2') or '').strip()
    ape1 = (request.POST.get('apellido1') or '').strip()
    ape2 = (request.POST.get('apellido2') or '').strip()
    correo = (request.POST.get('email') or '').strip()
    telefono = (request.POST.get('telefono') or '').strip()
    password = request.POST.get('password') or ''

    if not all([tipo_doc, numero, nom1, ape1, correo, telefono, password]):
        messages.error(request, 'Completa todos los campos obligatorios.')
        return render(request, 'registro.html', contexto)

    if not numero.isdigit() or not telefono.isdigit():
        messages.error(request, 'El documento y el teléfono deben ser numéricos.')
        return render(request, 'registro.html', contexto)

    if len(numero) > 18 or len(telefono) > 18:
        messages.error(request, 'El documento o el teléfono excede la longitud permitida.')
        return render(request, 'registro.html', contexto)

    try:
        validate_email(correo)
    except ValidationError:
        messages.error(request, 'Ingresa un correo electrónico válido.')
        return render(request, 'registro.html', contexto)
    if len(correo) > 45:
        messages.error(request, 'El correo no puede superar los 45 caracteres.')
        return render(request, 'registro.html', contexto)

    try:
        validate_password(
            password,
            user=SimpleNamespace(
                username=correo,
                email=correo,
                first_name=nom1,
                last_name=ape1,
            ),
        )
    except ValidationError as error:
        for mensaje in error.messages:
            messages.error(request, mensaje)
        return render(request, 'registro.html', contexto)

    documento = TipoDoc.objects.filter(
        id_doc=int(tipo_doc),
        estado=1,
    ).first()
    if not documento:
        messages.error(request, 'Selecciona un tipo de documento válido.')
        return render(request, 'registro.html', contexto)

    rol_cliente = _rol_cliente()
    if not rol_cliente:
        messages.error(request, 'No hay un rol de cliente configurado. Contacta al administrador.')
        return render(request, 'registro.html', contexto)

    if Persona.objects.filter(id_usuario=int(numero), pkfk_tipo_doc_id=int(tipo_doc)).exists():
        messages.error(request, 'Ya existe una persona con ese documento.')
        return render(request, 'registro.html', contexto)

    if Persona.objects.filter(correo_usu__iexact=correo).exists():
        messages.error(request, 'Ese correo ya está registrado.')
        return render(request, 'registro.html', contexto)

    with transaction.atomic(using='sistema'):
        Persona.objects.create(
            id_usuario=int(numero),
            pkfk_tipo_doc_id=int(tipo_doc),
            nom1_usu=nom1[:20],
            nom2_usu=(nom2[:20] if nom2 else None),
            ape1_usu=ape1[:20],
            ape2_usu=(ape2[:20] if ape2 else None),
            telefono=int(telefono),
            correo_usu=correo[:45],
            password=make_password(password),
            estado=1,
        )
        PersonaHasRol.objects.create(
            pkfk_id_usuario=int(numero),
            pkfk_tipo_doc=int(tipo_doc),
            pkfk_idrol_id=rol_cliente.idrol,
        )

    messages.success(request, 'Cuenta creada. Ya puedes iniciar sesión.')
    return redirect('login')


def _token_digest(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _reset_activo(token, now=None):
    if not token:
        return None
    return (
        PasswordResets.objects.using("sistema")
        .filter(
            token=_token_digest(token),
            codigo_hash__gt="",
            usado=0,
            intentos__lt=RESET_MAX_ATTEMPTS,
            expira__gt=now or timezone.now(),
        )
        .first()
    )


def recuperar_password_page(request):
    token = request.POST.get("token", "")
    if request.method == "POST" and token:
        reset = _reset_activo(token)
        if not reset:
            messages.error(
                request,
                "El enlace no es válido, venció o ya fue utilizado. Solicita uno nuevo.",
            )
            return redirect("recuperar_password")

        codigo = (request.POST.get("codigo") or "").strip()
        password = request.POST.get("password") or ""
        confirmacion = request.POST.get("confirmacion") or ""
        if not codigo.isdigit() or len(codigo) != 6:
            codigo = ""
        if not password or password != confirmacion:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect(f"{reverse('recuperar_password')}#token={token}")

        User = get_user_model()
        usuario_existente = User.objects.filter(
            email__iexact=reset.correo,
            is_active=True,
        ).first()
        try:
            validate_password(password, user=usuario_existente)
        except ValidationError as error:
            for mensaje in error.messages:
                messages.error(request, mensaje)
            return redirect(f"{reverse('recuperar_password')}#token={token}")

        with transaction.atomic(using="sistema"):
            reset = (
                PasswordResets.objects.using("sistema")
                .select_for_update()
                .filter(
                    pk=reset.pk,
                    usado=0,
                    intentos__lt=RESET_MAX_ATTEMPTS,
                    expira__gt=timezone.now(),
                )
                .first()
            )
            if not reset:
                messages.error(
                    request,
                    "El enlace no es válido, venció o ya fue utilizado. Solicita uno nuevo.",
                )
                return redirect("recuperar_password")

            if not codigo or not check_password(codigo, reset.codigo_hash):
                reset.intentos += 1
                if reset.intentos >= RESET_MAX_ATTEMPTS:
                    reset.usado = 1
                reset.save(using="sistema", update_fields=["intentos", "usado"])
                messages.error(
                    request,
                    "El código no es válido. Solicita un nuevo enlace si agotaste los intentos.",
                )
                return redirect(f"{reverse('recuperar_password')}#token={token}")

            personas = list(
                Persona.objects.using("sistema")
                .select_for_update()
                .filter(correo_usu__iexact=reset.correo, estado=1)
            )
            usuarios = list(
                User.objects.filter(email__iexact=reset.correo, is_active=True)
            )
            if not personas and not usuarios:
                reset.usado = 1
                reset.save(using="sistema", update_fields=["usado"])
                messages.error(request, "No se pudo completar la recuperación. Solicita un enlace nuevo.")
                return redirect("recuperar_password")

            hash_nuevo = make_password(password)
            for persona in personas:
                persona.password = hash_nuevo
                persona.save(using="sistema", update_fields=["password"])
            for usuario in usuarios:
                usuario.password = hash_nuevo
                usuario.save(using="default", update_fields=["password"])

            reset.usado = 1
            reset.save(using="sistema", update_fields=["usado"])
            PasswordResets.objects.using("sistema").filter(
                correo__iexact=reset.correo,
                usado=0,
            ).exclude(pk=reset.pk).update(usado=1)

        messages.success(request, "La contraseña se actualizó. Ya puedes iniciar sesión.")
        return redirect("login")

    return render(request, "seguimiento_pedidos/recuperar_password.html")


@require_POST
def api_enviar_recuperacion(request):
    try:
        if request.content_type and 'application/json' in request.content_type:
            data = json.loads(request.body.decode('utf-8'))
            correo = data.get('correo', '')
        else:
            correo = request.POST.get('correo', '')
    except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
        correo = ""

    correo = correo.strip().lower() if isinstance(correo, str) else ""
    try:
        validate_email(correo)
    except ValidationError:
        return JsonResponse({"ok": True, "mensaje": RESET_GENERIC_RESPONSE})
    if len(correo) > 120:
        return JsonResponse({"ok": True, "mensaje": RESET_GENERIC_RESPONSE})

    ahora = timezone.now()
    User = get_user_model()
    persona = Persona.objects.filter(correo_usu__iexact=correo, estado=1).first()
    usuario_django = User.objects.filter(
        email__iexact=correo,
        is_active=True,
    ).exclude(password__startswith="!").exists()
    if not persona and not usuario_django:
        return JsonResponse({"ok": True, "mensaje": RESET_GENERIC_RESPONSE})

    resets = PasswordResets.objects.using("sistema")
    if resets.filter(
        correo__iexact=correo,
        created_at__gte=ahora - RESET_REQUEST_COOLDOWN,
    ).exists():
        return JsonResponse({"ok": True, "mensaje": RESET_GENERIC_RESPONSE})

    token_plano = secrets.token_urlsafe(32)
    codigo_6_digitos = f"{secrets.randbelow(1_000_000):06d}"
    with transaction.atomic(using="sistema"):
        resets.filter(correo__iexact=correo, usado=0).update(usado=1)
        resets.create(
            correo=correo,
            token=_token_digest(token_plano),
            codigo="",
            codigo_hash=make_password(codigo_6_digitos),
            intentos=0,
            expira=ahora + RESET_EXPIRY,
            usado=0,
            created_at=ahora,
        )

    recovery_path = f"{reverse('recuperar_password')}#token={token_plano}"
    public_url = os.environ.get("SISPE_PUBLIC_URL", "").strip().rstrip("/")
    enlace_recuperacion = (
        f"{public_url}{recovery_path}"
        if public_url
        else request.build_absolute_uri(recovery_path)
    )
    asunto = 'Recuperación de contraseña - SISPE'
    nombre = persona.nom1_usu if persona else "usuario"
    cuerpo = (
        f'Hola {nombre},\n\n'
        f'Solicitaste recuperar tu contraseña en SISPE.\n'
        f'Código de verificación: {codigo_6_digitos}\n'
        f'Enlace de recuperación: {enlace_recuperacion}\n\n'
        f'Este código y enlace vencen en 15 minutos. Si no solicitaste este cambio, ignora este correo.'
    )
    cuerpo_html = render_to_string(
        "seguimiento_pedidos/emails/recuperar_password.html",
        {
            "nombre": nombre,
            "codigo": codigo_6_digitos,
            "enlace_recuperacion": enlace_recuperacion,
        },
    )

    try:
        send_mail(
            subject=asunto,
            message=cuerpo,
            from_email=None,
            recipient_list=[correo],
            html_message=cuerpo_html,
            fail_silently=False,
        )
    except (
        ImproperlyConfigured,
        OSError,
        UnicodeError,
        ValueError,
        smtplib.SMTPException,
    ) as error:
        resets.filter(token=_token_digest(token_plano)).update(usado=1)
        logger.error(
            "Password recovery email delivery failed (%s).",
            type(error).__name__,
        )
    return JsonResponse(
        {"ok": True, "mensaje": RESET_GENERIC_RESPONSE},
        status=200,
    )


# --- Dashboards de ejemplo por rol ---

@admin_required
def dashboard_admin(request):
    from datetime import date

    from django.db.models import F, Sum

    from administracion.models import Factura, Insumo
    from menu.models import Producto
    from mesas_pedidos.models import Mesa
    from pedidos.models import Pedido

    hoy = Factura.objects.filter(fecha__date=date.today(), estado='emitida')
    return render(request, 'seguimiento_pedidos/dashboards/admin.html', {
        'usuario': request.session.get('usuario_nombre', request.user.get_username()),
        'rol': 'Administrador',
        'ventas_hoy': hoy.aggregate(t=Sum('total'))['t'] or 0,
        'facturas_hoy': hoy.count(),
        'pedidos_activos': Pedido.objects.filter(estado__in=['pendiente', 'en_preparacion', 'listo']).count(),
        'mesas_ocupadas': Mesa.objects.filter(estado=Mesa.EstadoMesa.OCUPADA).count(),
        'mesas_total': Mesa.objects.count(),
        'insumos_bajos': Insumo.objects.filter(activo=True, stock_actual__lte=F('stock_minimo')).count(),
        'usuarios': Persona.objects.count(),
        'no_disponibles': Producto.objects.filter(disponible=False).count(),
    })


@rol_required('Chef', 'Cocinero')
def dashboard_cocinero(request):
    return render(request, 'seguimiento_pedidos/dashboards/cocinero.html', {
        'usuario': request.session.get('usuario_nombre', 'Cocinero'),
        'rol': 'Cocinero',
    })


@rol_required('Cajero')
def dashboard_cajero(request):
    from datetime import date
    from django.db.models import Sum
    from administracion.models import Factura
    from pedidos.models import Pedido
    from mesas_pedidos.models import Mesa

    hoy_inicio = date.today()
    facturas_hoy = Factura.objects.filter(fecha__date=hoy_inicio)
    recaudo_hoy = facturas_hoy.filter(estado='pagada').aggregate(t=Sum('total'))['t'] or 0
    facturas_emitidas = facturas_hoy.count()
    facturas_pagadas = facturas_hoy.filter(estado='pagada').count()
    facturas_pendientes = facturas_hoy.filter(estado='emitida').count()
    pedidos_activos = Pedido.objects.filter(estado__in=['pendiente', 'en_preparacion', 'listo']).count()

    return render(request, 'seguimiento_pedidos/dashboards/cajero.html', {
        'usuario': request.session.get('usuario_nombre', 'Cajero'),
        'rol': 'Cajero',
        'recaudo_hoy': recaudo_hoy,
        'facturas_emitidas': facturas_emitidas,
        'facturas_pagadas': facturas_pagadas,
        'facturas_pendientes': facturas_pendientes,
        'pedidos_activos': pedidos_activos,
    })


@rol_required('Mesero')
def dashboard_mesero(request):
    return render(request, 'seguimiento_pedidos/dashboards/mesero.html', {
        'usuario': request.session.get('usuario_nombre', 'Mesero'),
        'rol': 'Mesero',
    })


@login_required
def dashboard_cliente(request):
    return render(request, 'seguimiento_pedidos/dashboards/cliente.html', {
        'usuario': request.session.get('usuario_nombre', 'Cliente'),
        'rol': 'Cliente',
    })

    