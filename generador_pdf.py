from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape

from num2words import num2words
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle,
    Spacer,
    Image,
)

from configuracion import EMPRESA, MONEDA, IVA_PORCENTAJE, COLORES


def monto_en_letras(valor: float) -> str:
    entero = int(valor)
    centavos = int(round((valor - entero) * 100))
    letras = num2words(entero, lang="es").upper()
    return f"{letras} CON {centavos:02d}/100 USD"


def texto_seguro(texto: str) -> str:
    return escape(str(texto or "").strip())


def generar_pdf_cotizacion(datos: dict) -> bytes:
    """
    Genera la cotización en memoria y devuelve el PDF como bytes.
    """

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.3 * cm,
        rightMargin=1.3 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )

    styles = getSampleStyleSheet()

    azul = colors.HexColor(COLORES["azul"])
    gris_claro = colors.HexColor(COLORES["gris_claro"])
    gris_borde = colors.HexColor("#B8B8B8")

    estilo_normal = ParagraphStyle(
        "normal_cotizacion",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=10.5,
    )

    estilo_titulo = ParagraphStyle(
        "titulo_cotizacion",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=17,
        textColor=colors.white,
        alignment=1,
    )

    estilo_celda = ParagraphStyle(
        "celda_cotizacion",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        wordWrap="CJK",
    )

    story = []

    # TÍTULO
    titulo = Table(
        [[Paragraph("COTIZACIÓN", estilo_titulo)]],
        colWidths=[doc.width],
    )

    titulo.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), azul),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    story.append(titulo)
    story.append(Spacer(1, 8))

    # ENCABEZADO
    logo = ""

    if EMPRESA["logo_path"]:
        try:
            logo = Image(
                EMPRESA["logo_path"],
                width=3.8 * cm,
                height=2.2 * cm,
            )
        except Exception:
            logo = ""

    empresa_info = Paragraph(
        f"<b>{texto_seguro(EMPRESA['nombre'])}</b><br/>"
        f"RUC: {texto_seguro(EMPRESA['ruc'])}<br/>"
        f"{texto_seguro(EMPRESA['subtitulo'])}<br/>"
        f"{texto_seguro(EMPRESA['direccion'])}<br/>"
        f"Tel: {texto_seguro(EMPRESA['telefono'])}<br/>"
        f"Correo: {texto_seguro(EMPRESA['email'])}",
        estilo_normal,
    )

    fecha = datos.get("fecha") or datetime.now()

    cotizacion_info = Paragraph(
        f"<b>Número:</b> {texto_seguro(datos.get('numero', ''))}<br/>"
        f"<b>Fecha:</b> {fecha.strftime('%d/%m/%Y')}<br/>"
        f"<b>Moneda:</b> {MONEDA}",
        estilo_normal,
    )

    encabezado = Table(
        [[logo, empresa_info, cotizacion_info]],
        colWidths=[
            0.22 * doc.width,
            0.48 * doc.width,
            0.30 * doc.width,
        ],
    )

    encabezado.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.8, gris_borde),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    story.append(encabezado)
    story.append(Spacer(1, 8))

    # DATOS DEL CLIENTE
    cliente = Paragraph(
        "<b>DATOS DEL CLIENTE</b><br/>"
        f"<b>Cliente:</b> {texto_seguro(datos.get('cliente', ''))}<br/>"
        f"<b>RUC/CI:</b> {texto_seguro(datos.get('ruc', ''))}<br/>"
        f"<b>Dirección:</b> {texto_seguro(datos.get('direccion', ''))}<br/>"
        f"<b>Teléfono:</b> {texto_seguro(datos.get('telefono', ''))}<br/>"
        f"<b>Correo:</b> {texto_seguro(datos.get('correo', ''))}",
        estilo_normal,
    )

    cliente_tbl = Table([[cliente]], colWidths=[doc.width])

    cliente_tbl.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.8, gris_borde),
                ("BACKGROUND", (0, 0), (-1, -1), gris_claro),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    story.append(cliente_tbl)
    story.append(Spacer(1, 8))

    # TABLA DE ÍTEMS
    tabla = [
        [
            "ITEM",
            "CÓDIGO",
            "DESCRIPCIÓN",
            "UND",
            "CANT.",
            "P. UNIT.",
            "TOTAL",
        ]
    ]

    items = datos.get("items", [])

    for indice, item in enumerate(items, start=1):
        subtotal = float(item["cantidad"]) * float(item["precio"])

        tabla.append(
            [
                str(indice),
                Paragraph(texto_seguro(item.get("codigo", "")), estilo_celda),
                Paragraph(texto_seguro(item.get("descripcion", "")), estilo_celda),
                texto_seguro(item.get("unidad", "")),
                f"{float(item.get('cantidad', 0)):.2f}",
                f"{float(item.get('precio', 0)):.2f}",
                f"{subtotal:.2f}",
            ]
        )

    items_tbl = Table(
        tabla,
        repeatRows=1,
        colWidths=[
            0.06 * doc.width,
            0.13 * doc.width,
            0.37 * doc.width,
            0.08 * doc.width,
            0.10 * doc.width,
            0.12 * doc.width,
            0.14 * doc.width,
        ],
    )

    items_tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), azul),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("GRID", (0, 0), (-1, -1), 0.45, gris_borde),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    story.append(items_tbl)
    story.append(Spacer(1, 10))

    subtotal = float(datos.get("subtotal", 0))
    descuento = float(datos.get("descuento", 0))
    base_iva = max(subtotal - descuento, 0)
    iva = base_iva * IVA_PORCENTAJE if datos.get("aplica_iva", True) else 0
    total = base_iva + iva

    totales = Table(
        [
            ["", "SUBTOTAL:", f"{subtotal:.2f} {MONEDA}"],
            ["", "DESCUENTO:", f"{descuento:.2f} {MONEDA}"],
            ["", "IVA 15%:", f"{iva:.2f} {MONEDA}"],
            ["", "TOTAL:", f"{total:.2f} {MONEDA}"],
        ],
        colWidths=[
            0.56 * doc.width,
            0.22 * doc.width,
            0.22 * doc.width,
        ],
    )

    totales.setStyle(
        TableStyle(
            [
                ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
                ("FONTNAME", (1, -1), (-1, -1), "Helvetica-Bold"),
                ("LINEABOVE", (1, -1), (-1, -1), 0.8, gris_borde),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    story.append(totales)
    story.append(Spacer(1, 6))

    story.append(
        Paragraph(
            f"<b>SON:</b> {monto_en_letras(total)}",
            estilo_normal,
        )
    )

    story.append(Spacer(1, 10))

    condiciones = Paragraph(
        "<b>CONDICIONES COMERCIALES</b><br/><br/>"
        f"<b>Forma de pago:</b> {texto_seguro(datos.get('forma_pago', ''))}<br/>"
        f"<b>Tiempo de entrega:</b> {texto_seguro(datos.get('tiempo_entrega', ''))}<br/>"
        f"<b>Validez:</b> {texto_seguro(datos.get('validez', ''))}<br/>"
        f"<b>Lugar de entrega:</b> {texto_seguro(datos.get('lugar_entrega', ''))}<br/>"
        f"<b>Garantía:</b> {texto_seguro(datos.get('garantia', ''))}<br/>"
        f"<b>Observaciones:</b> {texto_seguro(datos.get('observaciones', ''))}",
        estilo_normal,
    )

    condiciones_tbl = Table([[condiciones]], colWidths=[doc.width])

    condiciones_tbl.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.8, gris_borde),
                ("BACKGROUND", (0, 0), (-1, -1), gris_claro),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    story.append(condiciones_tbl)

    doc.build(story)

    buffer.seek(0)
    return buffer.getvalue()