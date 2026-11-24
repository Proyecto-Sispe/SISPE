"""
CRUD funcional del menú dentro de la aplicación (no solo en el admin).

Cubre las cuatro entidades con las mismas cuatro operaciones:
    listar · crear · editar (modificar) · eliminar

La edición es la parte central: cada formulario se reutiliza para crear y para
modificar, así que cualquier campo —incluida la imagen— se puede cambiar después.
"""

from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from administracion.permisos import admin_required

from .forms import AdicionForm, CategoriaForm, ComboForm, ComboItemForm, ProductoForm
from .models import Adicion, Categoria, Combo, ComboItem, Producto


def _dinero(valor):
    try:
        return "$" + f"{valor:,.0f}".replace(",", ".")
    except (TypeError, ValueError):
        return "$0"


ENTIDADES = {
    "categorias": {
        "titulo": "Categorías",
        "singular": "categoría",
        "modelo": Categoria,
        "form": CategoriaForm,
        "pk": "id_categoria",
        "columnas": [
            ("nom_categoria", "Nombre"),
            ("orden", "Orden"),
            ("activa", "Visible"),
        ],
        "icono": "🍽️",
    },
    "productos": {
        "titulo": "Productos",
        "singular": "producto",
        "modelo": Producto,
        "form": ProductoForm,
        "pk": "id_menu",
        "columnas": [
            ("nombre", "Plato"),
            ("categoria", "Categoría"),
            ("precio", "Precio"),
            ("disponible", "Disponible"),
        ],
        "icono": "🍔",
        "con_foto": True,
    },
    "adiciones": {
        "titulo": "Adiciones",
        "singular": "adición",
        "modelo": Adicion,
        "form": AdicionForm,
        "pk": "id_adicion",
        "columnas": [
            ("nombre", "Adición"),
            ("precio", "Precio extra"),
            ("categoria", "Categoría"),
            ("activa", "Activa"),
        ],
        "icono": "➕",
    },
    "combos": {
        "titulo": "Combos",
        "singular": "combo",
        "modelo": Combo,
        "form": ComboForm,
        "pk": "id_combo",
        "columnas": [
            ("nombre", "Combo"),
            ("precio", "Precio"),
            ("precio_suelto", "Suma suelta"),
            ("activo", "Activo"),
        ],
        "icono": "🎁",
        "con_foto": True,
    },
}


def _config(entidad):
    if entidad not in ENTIDADES:
        from django.http import Http404

        raise Http404("Esa sección no existe")
    return ENTIDADES[entidad]


def _fila(entidad, obj):
    """Arma los valores de la tabla para una fila."""
    cfg = ENTIDADES[entidad]
    valores = []
    for campo, _etiqueta in cfg["columnas"]:
        if campo == "precio":
            valores.append(_dinero(getattr(obj, campo)))
        elif campo == "precio_suelto":
            valores.append(_dinero(obj.precio_suelto))
        elif campo == "categoria":
            cat = getattr(obj, "categoria", None)
            valores.append(cat.nom_categoria if cat else "Todas")
        elif campo in ("activa", "activo", "disponible"):
            valores.append(bool(getattr(obj, campo)))
        else:
            valores.append(getattr(obj, campo))
    return valores


@admin_required
def lista(request, entidad):
    cfg = _config(entidad)
    objetos = cfg["modelo"].objects.all()

    if entidad == "productos":
        objetos = objetos.select_related("categoria")
    if entidad == "adiciones":
        objetos = objetos.select_related("categoria")
    if entidad == "combos":
        objetos = objetos.prefetch_related("items__producto")

    filas = [
        {
            "obj": obj,
            "pk": getattr(obj, cfg["pk"]),
            "valores": _fila(entidad, obj),
        }
        for obj in objetos
    ]

    return render(
        request,
        "menu/gestion/lista.html",
        {
            "entidad": entidad,
            "cfg": cfg,
            "columnas": [c[1] for c in cfg["columnas"]],
            "filas": filas,
            "total": len(filas),
        },
    )


@admin_required
def crear(request, entidad):
    cfg = _config(entidad)
    if request.method == "POST":
        form = cfg["form"](request.POST, request.FILES)
        if form.is_valid():
            obj = form.save()
            messages.success(
                request, f"{cfg['singular'].capitalize()} creada correctamente."
            )
            if entidad == "combos":
                return redirect("gestion_combo_items", pk=obj.pk)
            return redirect("gestion_lista", entidad=entidad)
    else:
        form = cfg["form"]()

    return render(
        request,
        "menu/gestion/formulario.html",
        {"entidad": entidad, "cfg": cfg, "form": form, "modo": "crear", "objeto": None},
    )


@admin_required
def editar(request, entidad, pk):
    cfg = _config(entidad)
    obj = get_object_or_404(cfg["modelo"], **{cfg["pk"]: pk})

    if request.method == "POST":
        form = cfg["form"](request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"{cfg['singular'].capitalize()} actualizada correctamente."
            )
            if entidad == "combos":
                return redirect("gestion_combo_items", pk=obj.pk)
            return redirect("gestion_lista", entidad=entidad)
    else:
        form = cfg["form"](instance=obj)

    return render(
        request,
        "menu/gestion/formulario.html",
        {"entidad": entidad, "cfg": cfg, "form": form, "modo": "editar", "objeto": obj},
    )


@admin_required
def borrar(request, entidad, pk):
    cfg = _config(entidad)
    obj = get_object_or_404(cfg["modelo"], **{cfg["pk"]: pk})

    if request.method == "POST":
        try:
            obj.delete()
            messages.success(request, f"{cfg['singular'].capitalize()} eliminada.")
        except ProtectedError:
            messages.error(
                request,
                "No se puede eliminar: hay pedidos que usan este registro. "
                "Márcalo como inactivo en lugar de borrarlo.",
            )
        return redirect("gestion_lista", entidad=entidad)

    return render(
        request,
        "menu/gestion/borrar.html",
        {"entidad": entidad, "cfg": cfg, "objeto": obj},
    )


# --------------------------------------------------------------------------
# Partes del combo (modificar cada componente)
# --------------------------------------------------------------------------
@admin_required
def combo_items(request, pk):
    combo = get_object_or_404(Combo, pk=pk)
    editar_id = request.GET.get("editar")
    instancia = None
    if editar_id:
        instancia = get_object_or_404(ComboItem, pk=editar_id, combo=combo)

    if request.method == "POST":
        accion = request.POST.get("accion", "guardar")

        if accion == "quitar":
            item = get_object_or_404(
                ComboItem, pk=request.POST.get("item"), combo=combo
            )
            item.delete()
            messages.success(request, "Parte quitada del combo.")
            return redirect("gestion_combo_items", pk=combo.pk)

        item_id = request.POST.get("item_id")
        if item_id:
            item = get_object_or_404(ComboItem, pk=item_id, combo=combo)
            form = ComboItemForm(request.POST, instance=item)
        else:
            form = ComboItemForm(request.POST)

        if form.is_valid():
            parte = form.save(commit=False)
            parte.combo = combo
            parte.save()
            messages.success(request, "Parte del combo guardada.")
            return redirect("gestion_combo_items", pk=combo.pk)
    else:
        form = ComboItemForm(instance=instancia)

    return render(
        request,
        "menu/gestion/combo_items.html",
        {
            "combo": combo,
            "items": combo.items.select_related("producto"),
            "form": form,
            "editando": instancia,
        },
    )
