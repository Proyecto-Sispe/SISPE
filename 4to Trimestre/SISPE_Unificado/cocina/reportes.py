from io import BytesIO
from xml.sax.saxutils import escape

from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _filas_detalle(queryset):
    filas = []
    for detalle in queryset.iterator():
        filas.append(
            {
                "pedido": detalle.pedido_id,
                "fecha": detalle.pedido.fecha_pedido.strftime("%Y-%m-%d %H:%M"),
                "mesa": detalle.pedido.id_mesa,
                "estado": detalle.pedido.get_estado_display(),
                "tipo": "Combo" if detalle.combo_id else "Producto",
                "item": detalle.descripcion,
                "cantidad": detalle.cantidad,
                "precio_unitario": detalle.precio_unitario,
                "total": detalle.valor_venta,
            }
        )
    return filas


def _filas_excel(sheet, filas, encabezados):
    sheet.append(encabezados)
    for fila in filas:
        sheet.append(fila)
    for fila in sheet.iter_rows():
        for celda in fila:
            if isinstance(celda.value, str):
                celda.data_type = "s"
    for celda in sheet[1]:
        celda.fill = PatternFill(fill_type="solid", fgColor="FF7B00")
        celda.font = Font(bold=True, color="141414")
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    for columna in sheet.columns:
        ancho = max(
            (len(str(celda.value or "")) for celda in columna),
            default=10,
        )
        sheet.column_dimensions[columna[0].column_letter].width = min(ancho + 2, 42)


def exportar_excel(contexto):
    libro = Workbook()
    resumen = libro.active
    resumen.title = "Resumen"
    _filas_excel(
        resumen,
        [
            ["Desde", contexto["desde"] or "Sin límite"],
            ["Hasta", contexto["hasta"] or "Sin límite"],
            ["Categoría", contexto["categoria_nombre"]],
            ["Estado", contexto["estado_nombre"]],
            ["Ventas del filtro", contexto["ventas"]],
            ["Pedidos", contexto["cantidad_pedidos"]],
            ["Pedidos entregados", contexto["pedidos_entregados"]],
            ["Mesas ocupadas", contexto["mesas_ocupadas"]],
            ["Ticket promedio", contexto["ticket"]],
            ["Producto más vendido", contexto["producto_mas_vendido"]],
        ],
        ["Indicador", "Valor"],
    )

    por_categoria = libro.create_sheet("Por categoría")
    _filas_excel(
        por_categoria,
        [
            [
                fila["producto__categoria__nom_categoria"] or "Sin categoría",
                fila["unidades"],
                fila["total"],
            ]
            for fila in contexto["por_categoria"]
        ],
        ["Categoría", "Unidades", "Ventas"],
    )

    productos = libro.create_sheet("Productos")
    _filas_excel(
        productos,
        [
            [fila["producto__nombre"], fila["unidades"], fila["total"]]
            for fila in contexto["top"]
        ],
        ["Producto", "Unidades", "Ventas"],
    )

    combos = libro.create_sheet("Combos")
    _filas_excel(
        combos,
        [
            [fila["combo__nombre"], fila["unidades"], fila["total"]]
            for fila in contexto["combos_vendidos"]
        ],
        ["Combo", "Unidades", "Ventas"],
    )

    estados = libro.create_sheet("Estados")
    _filas_excel(
        estados,
        [[fila["estado"], fila["n"]] for fila in contexto["por_estado"]],
        ["Estado", "Pedidos"],
    )

    detalle = libro.create_sheet("Detalle")
    filas_detalle = _filas_detalle(contexto["detalle_export"])
    _filas_excel(
        detalle,
        [
            [
                fila["pedido"],
                fila["fecha"],
                fila["mesa"],
                fila["estado"],
                fila["tipo"],
                fila["item"],
                fila["cantidad"],
                fila["precio_unitario"],
                fila["total"],
            ]
            for fila in filas_detalle
        ],
        [
            "Pedido",
            "Fecha",
            "Mesa",
            "Estado",
            "Tipo",
            "Producto / combo",
            "Unidades",
            "Precio unitario",
            "Total",
        ],
    )
    salida = BytesIO()
    libro.save(salida)
    respuesta = HttpResponse(
        salida.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    respuesta["Content-Disposition"] = 'attachment; filename="reporte_sispe.xlsx"'
    return respuesta


def _tabla_pdf(filas, estilos, anchos=None):
    celdas = [
        [
            Paragraph(escape(str(valor)), estilos["CeldaReporte"])
            for valor in fila
        ]
        for fila in filas
    ]
    tabla = Table(celdas, colWidths=anchos, repeatRows=1, hAlign="LEFT")
    tabla.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ff7b00")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#141414")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#c7c7c7")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return tabla


def exportar_pdf(contexto):
    salida = BytesIO()
    documento = SimpleDocTemplate(
        salida,
        pagesize=landscape(A4),
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
        title="Reporte SISPE",
    )
    estilos = getSampleStyleSheet()
    estilos.add(
        ParagraphStyle(
            name="TituloSISPE",
            parent=estilos["Title"],
            textColor=colors.HexColor("#ff7b00"),
            alignment=TA_CENTER,
        )
    )
    estilos.add(
        ParagraphStyle(
            name="CeldaReporte",
            parent=estilos["BodyText"],
            fontName="Helvetica",
            fontSize=7,
            leading=9,
        )
    )
    elementos = [
        Paragraph("Reporte SISPE", estilos["TituloSISPE"]),
        Paragraph(
            "Fechas: "
            f"{escape(contexto['desde'] or 'sin límite')} a "
            f"{escape(contexto['hasta'] or 'sin límite')} · "
            f"Categoría: {escape(contexto['categoria_nombre'])} · "
            f"Estado: {escape(contexto['estado_nombre'])}",
            estilos["BodyText"],
        ),
        Spacer(1, 6 * mm),
        _tabla_pdf(
            [
                ["Indicador", "Resultado"],
                ["Ventas del filtro", f"${contexto['ventas']:,.0f}"],
                ["Pedidos", str(contexto["cantidad_pedidos"])],
                ["Pedidos entregados", str(contexto["pedidos_entregados"])],
                ["Mesas ocupadas", str(contexto["mesas_ocupadas"])],
                ["Ticket promedio", f"${contexto['ticket']:,.0f}"],
                ["Producto más vendido", contexto["producto_mas_vendido"]],
            ],
            estilos,
        ),
        Spacer(1, 6 * mm),
    ]

    secciones = [
        (
            "Ventas por categoría",
            [
                ["Categoría", "Unidades", "Ventas"],
                *[
                    [
                        fila["producto__categoria__nom_categoria"] or "Sin categoría",
                        fila["unidades"],
                        f"${fila['total']:,.0f}",
                    ]
                    for fila in contexto["por_categoria"]
                ],
            ],
        ),
        (
            "Productos más vendidos",
            [
                ["Producto", "Unidades", "Ventas"],
                *[
                    [fila["producto__nombre"], fila["unidades"], f"${fila['total']:,.0f}"]
                    for fila in contexto["top"]
                ],
            ],
        ),
        (
            "Combos vendidos",
            [
                ["Combo", "Unidades", "Ventas"],
                *[
                    [fila["combo__nombre"], fila["unidades"], f"${fila['total']:,.0f}"]
                    for fila in contexto["combos_vendidos"]
                ],
            ],
        ),
        (
            "Pedidos por estado",
            [
                ["Estado", "Pedidos"],
                *[[fila["estado"], fila["n"]] for fila in contexto["por_estado"]],
            ],
        ),
    ]
    for titulo, filas in secciones:
        if len(filas) == 1:
            filas.append(["Sin datos"] + [""] * (len(filas[0]) - 1))
        elementos.append(Paragraph(titulo, estilos["Heading2"]))
        elementos.append(_tabla_pdf(filas, estilos))
        elementos.append(Spacer(1, 5 * mm))

    filas_detalle = _filas_detalle(contexto["detalle_export"])
    tabla_detalle = [
        [
            "Pedido",
            "Fecha",
            "Mesa",
            "Estado",
            "Tipo",
            "Producto / combo",
            "Unidades",
            "Precio unitario",
            "Total",
        ],
        *[
            [
                fila["pedido"],
                fila["fecha"],
                fila["mesa"],
                fila["estado"],
                fila["tipo"],
                fila["item"],
                fila["cantidad"],
                f"${fila['precio_unitario']:,.0f}",
                f"${fila['total']:,.0f}",
            ]
            for fila in filas_detalle
        ],
    ]
    if len(tabla_detalle) == 1:
        tabla_detalle.append(["Sin datos"] + [""] * (len(tabla_detalle[0]) - 1))
    elementos.extend(
        [
            Paragraph("Detalle filtrado", estilos["Heading2"]),
            _tabla_pdf(
                tabla_detalle,
                estilos,
                [12 * mm, 24 * mm, 10 * mm, 20 * mm, 16 * mm, 55 * mm, 15 * mm, 24 * mm, 22 * mm],
            ),
        ]
    )

    documento.build(elementos)
    respuesta = HttpResponse(salida.getvalue(), content_type="application/pdf")
    respuesta["Content-Disposition"] = 'attachment; filename="reporte_sispe.pdf"'
    return respuesta
