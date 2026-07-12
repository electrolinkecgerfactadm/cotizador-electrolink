from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape

from num2words import num2words
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle,
    Spacer,
    Image,
)

from configuracion import (
    EMPRESA,
    MONEDA,
    IVA_PORCENTAJE,
    COLORES,
)


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def monto_en_letras(valor: float) -> str:
    entero = int(valor)

    centavos = int(
        round(
            (valor - entero) * 100
        )
    )

    letras = num2words(
        entero,
        lang="es",
    ).upper()

    return (
        f"{letras} CON "
        f"{centavos:02d}/100 USD"
    )


def texto_seguro(texto: str) -> str:
    return escape(
        str(texto or "").strip()
    )


def numero_seguro(valor) -> float:
    try:
        return float(valor)
    except (TypeError, ValueError):
        return 0.0


# =========================================================
# GENERADOR DEL PDF
# =========================================================

def generar_pdf_cotizacion(datos: dict) -> bytes:
    """
    Genera una cotización en PDF dentro de la memoria.

    Retorna:
        bytes: contenido completo del PDF.
    """

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.3 * cm,
        rightMargin=1.3 * cm,
        topMargin=1.0 * cm,
        bottomMargin=1.0 * cm,
    )

    styles = getSampleStyleSheet()

    azul = colors.HexColor(
        COLORES["azul"]
    )

    gris_claro = colors.HexColor(
        COLORES["gris_claro"]
    )

    gris_borde = colors.HexColor(
        "#B8B8B8"
    )

    gris_texto = colors.HexColor(
        "#333333"
    )

    # =====================================================
    # ESTILOS
    # =====================================================

    estilo_normal = ParagraphStyle(
        "normal_cotizacion",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=10.5,
        textColor=gris_texto,
    )

    estilo_pequeno = ParagraphStyle(
        "pequeno_cotizacion",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.6,
        leading=9.2,
        textColor=gris_texto,
        wordWrap="CJK",
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
        leading=9.5,
        textColor=gris_texto,
        wordWrap="CJK",
    )

    estilo_celda_centro = ParagraphStyle(
        "celda_centro_cotizacion",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=9.5,
        textColor=gris_texto,
        alignment=1,
        wordWrap="CJK",
    )

    estilo_condicion_titulo = ParagraphStyle(
        "titulo_condiciones",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        alignment=1,
        textColor=gris_texto,
    )

    estilo_condicion_label = ParagraphStyle(
        "label_condiciones",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.2,
        textColor=gris_texto,
    )

    estilo_condicion_texto = ParagraphStyle(
        "texto_condiciones",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=9.2,
        textColor=gris_texto,
        wordWrap="CJK",
    )

    story = []

    # =====================================================
    # TÍTULO PRINCIPAL
    # =====================================================

    titulo = Table(
        [
            [
                Paragraph(
                    "COTIZACIÓN",
                    estilo_titulo,
                )
            ]
        ],
        colWidths=[doc.width],
    )

    titulo.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    azul,
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
            ]
        )
    )

    story.append(titulo)
    story.append(Spacer(1, 8))

    # =====================================================
    # ENCABEZADO EMPRESA
    # =====================================================

    logo = ""

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

    fecha = datos.get(
        "fecha",
        datetime.now(),
    )

    if not isinstance(
        fecha,
        datetime,
    ):
        fecha = datetime.now()

    cotizacion_info = Paragraph(
        f"<b>Número:</b> "
        f"{texto_seguro(datos.get('numero', ''))}<br/>"
        f"<b>Fecha:</b> "
        f"{fecha.strftime('%d/%m/%Y')}<br/>"
        f"<b>Moneda:</b> "
        f"{texto_seguro(MONEDA)}",
        estilo_normal,
    )

    encabezado = Table(
        [
            [
                logo,
                empresa_info,
                cotizacion_info,
            ]
        ],
        colWidths=[
            0.22 * doc.width,
            0.48 * doc.width,
            0.30 * doc.width,
        ],
    )

    encabezado.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    gris_borde,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
            ]
        )
    )

    story.append(encabezado)
    story.append(Spacer(1, 8))

    # =====================================================
    # DATOS DEL CLIENTE
    # =====================================================

    cliente = Paragraph(
        "<b>DATOS DEL CLIENTE</b><br/>"
        f"<b>Cliente:</b> "
        f"{texto_seguro(datos.get('cliente', ''))}<br/>"
        f"<b>RUC/CI:</b> "
        f"{texto_seguro(datos.get('ruc', ''))}<br/>"
        f"<b>Dirección:</b> "
        f"{texto_seguro(datos.get('direccion', ''))}<br/>"
        f"<b>Teléfono:</b> "
        f"{texto_seguro(datos.get('telefono', ''))}<br/>"
        f"<b>Correo:</b> "
        f"{texto_seguro(datos.get('correo', ''))}",
        estilo_normal,
    )

    cliente_tbl = Table(
        [[cliente]],
        colWidths=[doc.width],
    )

    cliente_tbl.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    gris_borde,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    gris_claro,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
            ]
        )
    )

    story.append(cliente_tbl)
    story.append(Spacer(1, 8))

    # =====================================================
    # TABLA DE PRODUCTOS
    # =====================================================

    tabla_items = [
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

    items = datos.get(
        "items",
        [],
    )

    for indice, item in enumerate(
        items,
        start=1,
    ):
        cantidad = numero_seguro(
            item.get(
                "cantidad",
                0,
            )
        )

        precio = numero_seguro(
            item.get(
                "precio",
                0,
            )
        )

        subtotal_item = (
            cantidad * precio
        )

        descripcion = texto_seguro(
            item.get(
                "descripcion",
                "",
            )
        )

        marca = texto_seguro(
            item.get(
                "marca",
                "",
            )
        )

        if marca:
            descripcion_completa = (
                f"{descripcion}<br/>"
                f"<b>Marca:</b> {marca}"
            )
        else:
            descripcion_completa = descripcion

        tabla_items.append(
            [
                Paragraph(
                    str(indice),
                    estilo_celda_centro,
                ),
                Paragraph(
                    texto_seguro(
                        item.get(
                            "codigo",
                            "",
                        )
                    ),
                    estilo_celda,
                ),
                Paragraph(
                    descripcion_completa,
                    estilo_celda,
                ),
                Paragraph(
                    texto_seguro(
                        item.get(
                            "unidad",
                            "",
                        )
                    ),
                    estilo_celda_centro,
                ),
                Paragraph(
                    f"{cantidad:.2f}",
                    estilo_celda_centro,
                ),
                Paragraph(
                    f"{precio:.2f}",
                    estilo_celda_centro,
                ),
                Paragraph(
                    f"{subtotal_item:.2f}",
                    estilo_celda_centro,
                ),
            ]
        )

    items_tbl = Table(
        tabla_items,
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
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    azul,
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, 0),
                    8,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.45,
                    gris_borde,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, 0),
                    "CENTER",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )
    )

    story.append(items_tbl)
    story.append(Spacer(1, 8))

    # =====================================================
    # TOTALES
    # =====================================================

    subtotal = numero_seguro(
        datos.get(
            "subtotal",
            0,
        )
    )

    descuento = numero_seguro(
        datos.get(
            "descuento",
            0,
        )
    )

    base_iva = max(
        subtotal - descuento,
        0,
    )

    aplica_iva = datos.get(
        "aplica_iva",
        True,
    )

    iva = (
        base_iva
        * IVA_PORCENTAJE
        if aplica_iva
        else 0
    )

    total = base_iva + iva

    texto_iva = (
        f"IVA "
        f"{IVA_PORCENTAJE * 100:.0f}%:"
    )

    totales = Table(
        [
            [
                "",
                "SUBTOTAL:",
                f"{subtotal:.2f} {MONEDA}",
            ],
            [
                "",
                "DESCUENTO:",
                f"{descuento:.2f} {MONEDA}",
            ],
            [
                "",
                texto_iva,
                f"{iva:.2f} {MONEDA}",
            ],
            [
                "",
                "TOTAL:",
                f"{total:.2f} {MONEDA}",
            ],
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
                (
                    "ALIGN",
                    (2, 0),
                    (-1, -1),
                    "RIGHT",
                ),
                (
                    "FONTNAME",
                    (1, -1),
                    (-1, -1),
                    "Helvetica-Bold",
                ),
                (
                    "LINEABOVE",
                    (1, -1),
                    (-1, -1),
                    0.8,
                    gris_borde,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    story.append(totales)
    story.append(Spacer(1, 5))

    story.append(
        Paragraph(
            f"<b>SON:</b> "
            f"{monto_en_letras(total)}",
            estilo_normal,
        )
    )

    story.append(Spacer(1, 8))

    # =====================================================
    # CONDICIONES COMERCIALES
    # =====================================================

    story.append(
        Paragraph(
            "CONDICIONES COMERCIALES",
            estilo_condicion_titulo,
        )
    )

    story.append(Spacer(1, 3))

    validez = texto_seguro(
        datos.get(
            "validez",
            "7 DÍAS",
        )
    )

    tiempo_entrega = texto_seguro(
        datos.get(
            "tiempo_entrega",
            "EL PLAZO DE ENTREGA SERÁ "
            "ACORDADO CON EL CLIENTE",
        )
    )

    lugar_entrega = texto_seguro(
        datos.get(
            "lugar_entrega",
            "EL SITIO INDICADO POR EL CLIENTE",
        )
    )

    forma_pago = texto_seguro(
        datos.get(
            "forma_pago",
            "TRANSFERENCIA",
        )
    )

    garantia = texto_seguro(
        datos.get(
            "garantia",
            "SEGÚN FABRICANTE",
        )
    )

    observaciones = texto_seguro(
        datos.get(
            "observaciones",
            "",
        )
    )

    condiciones_data = [
        [
            Paragraph(
                "Validez de la cotización:",
                estilo_condicion_label,
            ),
            Paragraph(
                f"La cotización tiene una validez de "
                f"{validez} a partir de la fecha de emisión. "
                f"Después de este plazo, los precios y condiciones "
                f"podrán ser modificados sin previo aviso.",
                estilo_condicion_texto,
            ),
        ],
        [
            Paragraph(
                "Tiempo de entrega:",
                estilo_condicion_label,
            ),
            Paragraph(
                f"{tiempo_entrega}. "
                f"El plazo puede variar en función de la "
                f"disponibilidad de los productos.",
                estilo_condicion_texto,
            ),
        ],
        [
            Paragraph(
                "Sitio de entrega:",
                estilo_condicion_label,
            ),
            Paragraph(
                f"La entrega se realizará en {lugar_entrega}. "
                f"Cualquier cambio en el destino debe ser "
                f"comunicado por escrito.",
                estilo_condicion_texto,
            ),
        ],
        [
            Paragraph(
                "Forma de pago:",
                estilo_condicion_label,
            ),
            Paragraph(
                forma_pago,
                estilo_condicion_texto,
            ),
        ],
        [
            Paragraph(
                "Cuenta:",
                estilo_condicion_label,
            ),
            Paragraph(
                "Banco Produbanco, Cuenta Corriente, "
                "Nro. 02006210623, Electrolink S.A.S.",
                estilo_condicion_texto,
            ),
        ],
        [
            Paragraph(
                "Notificaciones de pago:",
                estilo_condicion_label,
            ),
            Paragraph(
                "facturacion@electrolinkec.com",
                estilo_condicion_texto,
            ),
        ],
        [
            Paragraph(
                "Despacho/Envío:",
                estilo_condicion_label,
            ),
            Paragraph(
                "El despacho de la mercadería se realizará una vez "
                "que se confirme la EFECTIVIZACIÓN del pago mediante "
                "transferencia o depósito hasta las 16:00 del mismo día.",
                estilo_condicion_texto,
            ),
        ],
        [
            Paragraph(
                "Costo de envío:",
                estilo_condicion_label,
            ),
            Paragraph(
                "El costo de envío será totalmente asumido por el cliente. "
                "Los costos de envío no están incluidos en la cotización.",
                estilo_condicion_texto,
            ),
        ],
        [
            Paragraph(
                "Cambios y cancelaciones:",
                estilo_condicion_label,
            ),
            Paragraph(
                "Una vez generada y aprobada la orden de compra, "
                "no se aceptan cambios, cancelaciones ni devoluciones "
                "bajo ningún concepto.",
                estilo_condicion_texto,
            ),
        ],
        [
            Paragraph(
                "Garantía:",
                estilo_condicion_label,
            ),
            Paragraph(
                f"{garantia}. La presente garantía cubre exclusivamente "
                f"defectos de fabricación en los equipos suministrados. "
                f"No aplica a daños ocasionados por uso indebido, "
                f"desgaste natural, instalación inadecuada o factores "
                f"externos ajenos al proceso de fabricación.",
                estilo_condicion_texto,
            ),
        ],
        [
            Paragraph(
                "Incumplimiento:",
                estilo_condicion_label,
            ),
            Paragraph(
                "En caso de incumplimiento en los pagos, la empresa "
                "se reserva el derecho de suspender la entrega o "
                "rescindir el contrato sin previo aviso.",
                estilo_condicion_texto,
            ),
        ],
    ]

    if observaciones:
        condiciones_data.append(
            [
                Paragraph(
                    "Observaciones:",
                    estilo_condicion_label,
                ),
                Paragraph(
                    observaciones,
                    estilo_condicion_texto,
                ),
            ]
        )

    condiciones_tbl = Table(
        condiciones_data,
        colWidths=[
            0.28 * doc.width,
            0.72 * doc.width,
        ],
    )

    condiciones_tbl.setStyle(
        TableStyle(
            [
                (
                    "LINEABOVE",
                    (0, 0),
                    (-1, 0),
                    0.7,
                    gris_borde,
                ),
                (
                    "LINEBELOW",
                    (0, -1),
                    (-1, -1),
                    0.7,
                    gris_borde,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    2.5,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    2.5,
                ),
            ]
        )
    )

    story.append(condiciones_tbl)
    story.append(Spacer(1, 12))

    # =====================================================
    # DESPEDIDA Y FIRMA
    # =====================================================

    despedida = Paragraph(
        "<b>Cordialmente,</b><br/>"
        "ELECTROLINKEC",
        estilo_normal,
    )

    story.append(despedida)


    # =====================================================
    # CREAR PDF
    # =====================================================

    doc.build(story)

    buffer.seek(0)

    return buffer.getvalue()