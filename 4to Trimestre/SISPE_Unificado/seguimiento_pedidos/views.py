import hashlib
import json
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from administracion.permisos import DJANGO_DASHBOARD_GROUP, admin_required, rol_required

from .models import PasswordResets, Persona, PersonaHasRol, Rol, TipoDoc


def _verificar_password(password_ingresada, password_bd):
    if not password_bd:
        return False
    # Soporta contraseñas hasheadas de Django y texto plano inicial del SQL
    if password_bd.startswith(('pbkdf2_', 'argon2$', 'bcrypt$')):
        return check_password(password_ingresada, password_bd)
    return password_ingresada == password_bd


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


def _usuario_django(persona, rol):
    """Crea o actualiza el usuario de Django que acompana a la persona SISPE."""
    User = get_user_model()
    usuario, creado = User.objects.get_or_create(username=persona.correo_usu.lower())
    if creado:
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

        persona = Persona.objects.filter(
            correo_usu__iexact=identificador,
            estado=1,
        ).first()

        if persona and _verificar_password(password, persona.password):
            rol = _obtener_rol_usuario(persona)
            if not rol or rol not in RUTAS_POR_ROL:
                messages.error(request, 'El usuario no tiene un rol valido asignado.')
                return _pantalla_login(request)

            auth_login(request, _usuario_django(persona, rol))
            request.session['usuario_id'] = persona.id_usuario
            request.session['usuario_tipo_doc'] = persona.pkfk_tipo_doc_id
            request.session['usuario_nombre'] = f'{persona.nom1_usu} {persona.ape1_usu}'
            request.session['usuario_rol'] = rol
            return redirect(siguiente or RUTAS_POR_ROL[rol])

        usuario = authenticate(request, username=identificador, password=password)
        if usuario is not None:
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

        messages.error(request, 'Correo/usuario o contrasena incorrectos.')
        return _pantalla_login(request)

    return _pantalla_login(request)


def logout_view(request):
    auth_logout(request)
    return redirect('home')


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


def recuperar_password_page(request):
    return render(request, 'seguimiento_pedidos/recuperar_password.html')


@csrf_exempt
@require_POST
def api_enviar_recuperacion(request):
    try:
        if request.content_type and 'application/json' in request.content_type:
            data = json.loads(request.body.decode('utf-8'))
            correo = data.get('correo', '').strip().lower()
        else:
            correo = request.POST.get('correo', '').strip().lower()
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'ok': False, 'mensaje': 'JSON inválido.'}, status=400)

    if not correo:
        return JsonResponse({'ok': False, 'mensaje': 'Debes ingresar un correo.'}, status=400)

    persona = Persona.objects.filter(correo_usu__iexact=correo, estado=1).first()
    if not persona:
        return JsonResponse(
            {'ok': False, 'mensaje': 'No existe un usuario activo con ese correo.'},
            status=404,
        )

    token_plano = get_random_string(40)
    token_hash = hashlib.sha256(token_plano.encode('utf-8')).hexdigest()
    codigo_6_digitos = get_random_string(6, allowed_chars='0123456789')
    ahora = timezone.now()
    expira = ahora + timedelta(minutes=15)

    PasswordResets.objects.create(
        correo=persona.correo_usu,
        token=token_hash,
        codigo=codigo_6_digitos,
        expira=expira,
        usado=0,
        created_at=ahora,
    )

    enlace_recuperacion = request.build_absolute_uri(
        f'/recuperar-password/?token={token_plano}'
    )

    asunto = 'Recuperación de contraseña - SISPE'
    cuerpo = (
        f'Hola {persona.nom1_usu},\n\n'
        f'Solicitaste recuperar tu contraseña en SISPE.\n'
        f'Código de verificación: {codigo_6_digitos}\n'
        f'Enlace de recuperación: {enlace_recuperacion}\n\n'
        f'Este código y enlace vencen en 15 minutos.'
    )

    try:
        send_mail(
            subject=asunto,
            message=cuerpo,
            from_email=None,
            recipient_list=[persona.correo_usu],
            fail_silently=False,
        )
    except Exception as exc:
        return JsonResponse(
            {'ok': False, 'mensaje': f'No se pudo enviar el correo: {exc}'},
            status=500,
        )

    return JsonResponse(
        {
            'ok': True,
            'mensaje': 'Correo de recuperación enviado correctamente.',
            'expira_en_minutos': 15,
        },
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

    