from django.shortcuts import redirect, render
from django.db import transaction
from django.contrib import messages

from .forms import CargaMasivaForm
from .models import HistorialCarga
from .services import leer_archivo, validar_filas

from administracion.permisos import admin_required

from menu.models import Categoria, Producto
from administracion.models import Insumo


@admin_required
def inicio(request):

    contexto = {
        "form": CargaMasivaForm(),
        "historial": HistorialCarga.objects.all()[:10],
    }

    if request.method == "POST":

        form = CargaMasivaForm(request.POST, request.FILES)

        if form.is_valid():

            archivo = form.cleaned_data["archivo"]
            tipo = form.cleaned_data["tipo"]
            accion = request.POST.get("accion")

            try:

                filas = leer_archivo(archivo)

                registros, errores = validar_filas(
                    tipo,
                    filas
                )

                if accion == "previsualizar":

                    contexto.update({
                        "form": form,
                        "registros": registros[:100],
                        "errores": errores,
                        "total": len(filas),
                        "correctos": len(registros),
                        "archivo_nombre": archivo.name,
                        "tipo": tipo,
                    })

                    return render(
                        request,
                        "carga_masiva/inicio.html",
                        contexto
                    )

                elif accion == "importar":

                    if not registros:

                        messages.error(
                            request,
                            "No hay registros válidos para importar. Corrige los errores y vuelve a validar."
                        )

                        HistorialCarga.objects.create(
                            usuario=request.user,
                            tipo=tipo,
                            archivo_nombre=archivo.name,
                            total_registros=len(filas),
                            registros_exitosos=0,
                            registros_error=len(errores),
                            estado="fallida",
                        )

                        contexto.update({
                            "form": form,
                            "registros": registros,
                            "errores": errores,
                            "total": len(filas),
                            "correctos": 0,
                            "archivo_nombre": archivo.name,
                            "tipo": tipo,
                        })

                    else:
                        with transaction.atomic(using="default"):

                            for registro in registros:

                                if tipo == "categorias":

                                    Categoria.objects.using(
                                        "default"
                                    ).create(
                                        nom_categoria=registro["nombre"]
                                    )

                                elif tipo == "productos":

                                    Producto.objects.using(
                                        "default"
                                    ).create(
                                        nombre=registro["nombre"],
                                        descripcion=registro["descripcion"],
                                        precio=registro["precio"],
                                        categoria=registro["categoria"],
                                        disponible=registro["disponible"],
                                        orden=registro["orden"],
                                    )

                                elif tipo == "insumos":

                                    Insumo.objects.using(
                                        "default"
                                    ).create(**registro)

                            HistorialCarga.objects.create(
                                usuario=request.user,
                                tipo=tipo,
                                archivo_nombre=archivo.name,
                                total_registros=len(filas),
                                registros_exitosos=len(registros),
                                registros_error=len(errores),
                                estado="exitosa",
                            )

                        messages.success(
                            request,
                            f"Se importaron {len(registros)} registros correctamente."
                        )

                        if errores:
                            messages.warning(
                                request,
                                f"Se omitieron {len(errores)} registros con errores. Revisa el detalle de validación."
                            )
                        return redirect("carga_masiva_inicio")

            except Exception as error:

                messages.error(
                    request,
                    f"No fue posible procesar el archivo: {error}"
                )

        contexto.update({
            "form": form,
            "historial": HistorialCarga.objects.all()[:10],
        })

    return render(
        request,
        "carga_masiva/inicio.html",
        contexto
    )