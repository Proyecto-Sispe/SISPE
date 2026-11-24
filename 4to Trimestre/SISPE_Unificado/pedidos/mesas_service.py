"""Servicios para sincronizar el estado de las mesas y sesiones en todas las bases de datos."""

from django.utils import timezone


def liberar_mesa_y_sesion(id_mesa):
    """
    Libera la mesa asociada y cierra cualquier sesión de mesa activa
    en las bases de datos del sistema (mesas y sistema).
    """
    if not id_mesa:
        return
    try:
        mesa_num = int(id_mesa)
    except (ValueError, TypeError):
        return

    # 1. Base 'mesas' (Victor / mesas_pedidos)
    try:
        from mesas_pedidos.models import Mesa, SesionMesa
        Mesa.objects.filter(pk=mesa_num).update(estado=Mesa.EstadoMesa.LIBRE)
        SesionMesa.objects.filter(mesa_id=mesa_num, activa=True).update(
            activa=False, fecha_fin=timezone.now()
        )
    except Exception:
        pass

    # 2. Base 'sistema' (Juan / base_datos y Sispe / seguimiento_pedidos)
    try:
        from base_datos.models import Mesa as MesaBD, SesionMesa as SesionBD
        MesaBD.objects.filter(id_mesa=mesa_num).update(estado=0)
        SesionBD.objects.filter(id_mesa=mesa_num, activa=1).update(
            activa=0, fecha_fin=timezone.now()
        )
    except Exception:
        pass

    try:
        from seguimiento_pedidos.models import Mesa as MesaSeg, SesionMesa as SesionSeg
        MesaSeg.objects.filter(id_mesa=mesa_num).update(estado=0)
        SesionSeg.objects.filter(id_mesa=mesa_num, activa=1).update(
            activa=0, fecha_fin=timezone.now()
        )
    except Exception:
        pass


def ocupar_mesa(id_mesa):
    """Marca la mesa como ocupada en las bases correspondientes."""
    if not id_mesa:
        return
    try:
        mesa_num = int(id_mesa)
    except (ValueError, TypeError):
        return

    try:
        from mesas_pedidos.models import Mesa
        Mesa.objects.filter(pk=mesa_num).update(estado=Mesa.EstadoMesa.OCUPADA)
    except Exception:
        pass

    try:
        from base_datos.models import Mesa as MesaBD
        MesaBD.objects.filter(id_mesa=mesa_num).update(estado=1)
    except Exception:
        pass

    try:
        from seguimiento_pedidos.models import Mesa as MesaSeg
        MesaSeg.objects.filter(id_mesa=mesa_num).update(estado=1)
    except Exception:
        pass
