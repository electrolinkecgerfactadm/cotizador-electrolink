from datetime import datetime

import streamlit as st

from generador_pdf import generar_pdf_cotizacion

from historial_cotizaciones import (
    guardar_cotizacion,
    buscar_cotizaciones,
    eliminar_cotizacion,
)


# =========================================================
# CONFIGURACIÓN DE LA PÁGINA
# =========================================================

st.set_page_config(
    page_title="Cotizador Electrolink",
    page_icon="⚡",
    layout="centered",
)


# =========================================================
# ESTILOS
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1000px;
        padding-top: 4rem;
        padding-bottom: 2rem;
    }

    .titulo-principal {
        color: #004FAF;
        font-size: 2.3rem;
        font-weight: 700;
        margin-top: 0.5rem;
        margin-bottom: 0.2rem;
        line-height: 1.2;
    }

    .subtitulo {
        color: #6D6D6E;
        font-size: 1.05rem;
        margin-bottom: 1.2rem;
    }

    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
    }

    div.stDownloadButton > button {
        width: 100%;
        border-radius: 8px;
        background-color: #004FAF;
        color: white;
        font-weight: 700;
    }

    div[role="radiogroup"] {
        display: flex;
        gap: 16px;
        width: 100%;
        margin-bottom: 18px;
    }

    div[role="radiogroup"] label {
        flex: 1;
        min-height: 64px;
        background-color: #F2F4F8;
        border: 2px solid #004FAF;
        border-radius: 12px;
        padding: 14px 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
    }

    div[role="radiogroup"] label p {
        font-size: 19px !important;
        font-weight: 700 !important;
        color: #004FAF !important;
        margin: 0 !important;
        text-align: center;
    }

    div[role="radiogroup"] label:has(input:checked) {
        background-color: #004FAF !important;
        border-color: #004FAF !important;
    }

    div[role="radiogroup"] label:has(input:checked) p {
        color: white !important;
    }

    div[data-testid="stExpander"] {
        border-radius: 10px;
        margin-bottom: 10px;
    }

    div[data-testid="stExpander"] details summary {
        font-size: 17px !important;
        font-weight: 600 !important;
        padding-top: 10px !important;
        padding-bottom: 10px !important;
    }

    @media (max-width: 700px) {

        .block-container {
            padding-top: 2.5rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }

        .titulo-principal {
            font-size: 1.8rem;
        }

        div[role="radiogroup"] {
            gap: 8px;
        }

        div[role="radiogroup"] label {
            min-height: 58px;
            padding: 10px 8px;
        }

        div[role="radiogroup"] label p {
            font-size: 14px !important;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ESTADO DE LA APLICACIÓN
# =========================================================

if "items_cotizacion" not in st.session_state:
    st.session_state["items_cotizacion"] = []

if "modo_edicion" not in st.session_state:
    st.session_state["modo_edicion"] = False

if "numero_original_edicion" not in st.session_state:
    st.session_state["numero_original_edicion"] = ""

if "fecha_cotizacion" not in st.session_state:
    st.session_state["fecha_cotizacion"] = datetime.now().date()


# =========================================================
# FUNCIÓN PARA CARGAR UNA COTIZACIÓN Y EDITARLA
# =========================================================

def cargar_cotizacion_para_editar(cotizacion):

    numero_original = str(
        cotizacion.get(
            "numero",
            "",
        )
    ).strip()

    st.session_state[
        "numero_original_edicion"
    ] = numero_original

    st.session_state[
        "numero_cotizacion"
    ] = numero_original

    fecha_texto = str(
        cotizacion.get(
            "fecha",
            "",
        )
    )

    try:
        fecha_edicion = datetime.strptime(
            fecha_texto,
            "%Y-%m-%d",
        ).date()

    except Exception:
        fecha_edicion = datetime.now().date()

    st.session_state[
        "fecha_cotizacion"
    ] = fecha_edicion

    st.session_state["cliente"] = str(
        cotizacion.get(
            "cliente",
            "",
        )
    )

    st.session_state["ruc_cliente"] = str(
        cotizacion.get(
            "ruc",
            "",
        )
    )

    st.session_state["direccion_cliente"] = str(
        cotizacion.get(
            "direccion",
            "",
        )
    )

    st.session_state["telefono_cliente"] = str(
        cotizacion.get(
            "telefono",
            "",
        )
    )

    st.session_state["correo_cliente"] = str(
        cotizacion.get(
            "correo",
            "",
        )
    )

    st.session_state[
        "items_cotizacion"
    ] = [
        dict(item)
        for item in cotizacion.get(
            "items",
            [],
        )
    ]

    st.session_state[
        "descuento_total"
    ] = float(
        cotizacion.get(
            "descuento",
            0,
        )
    )

    st.session_state[
        "aplica_iva"
    ] = bool(
        cotizacion.get(
            "aplica_iva",
            True,
        )
    )

    formas_pago_validas = [
        "CONTADO",
        "CRÉDITO 15 DÍAS",
        "CRÉDITO 30 DÍAS",
        "CRÉDITO 45 DÍAS",
        "CRÉDITO 60 DÍAS",
        "POR DEFINIR",
    ]

    forma_pago_guardada = str(
        cotizacion.get(
            "forma_pago",
            "CONTADO",
        )
    )

    if (
        forma_pago_guardada
        not in formas_pago_validas
    ):
        forma_pago_guardada = "POR DEFINIR"

    st.session_state[
        "forma_pago"
    ] = forma_pago_guardada

    st.session_state[
        "tiempo_entrega"
    ] = str(
        cotizacion.get(
            "tiempo_entrega",
            "ENTREGA INMEDIATA",
        )
    )

    st.session_state[
        "validez_oferta"
    ] = str(
        cotizacion.get(
            "validez",
            "7 DÍAS",
        )
    )

    st.session_state[
        "lugar_entrega"
    ] = str(
        cotizacion.get(
            "lugar_entrega",
            "QUITO",
        )
    )

    st.session_state[
        "garantia"
    ] = str(
        cotizacion.get(
            "garantia",
            "SEGÚN FABRICANTE",
        )
    )

    st.session_state[
        "observaciones"
    ] = str(
        cotizacion.get(
            "observaciones",
            "",
        )
    )

    st.session_state[
        "modo_edicion"
    ] = True

    st.session_state[
        "seccion_principal"
    ] = "NUEVA COTIZACIÓN"


# =========================================================
# ENCABEZADO
# =========================================================

st.markdown(
    '<div class="titulo-principal">'
    'COTIZADOR ELECTROLINK'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitulo">'
    'Generación rápida de cotizaciones en PDF'
    '</div>',
    unsafe_allow_html=True,
)


# =========================================================
# NAVEGACIÓN
# =========================================================

seccion = st.radio(
    "SECCIÓN",
    options=[
        "NUEVA COTIZACIÓN",
        "COTIZACIONES REALIZADAS",
    ],
    horizontal=True,
    label_visibility="collapsed",
    key="seccion_principal",
)


# =========================================================
# COTIZACIONES REALIZADAS
# =========================================================

if seccion == "COTIZACIONES REALIZADAS":

    st.markdown("---")

    st.subheader(
        "COTIZACIONES REALIZADAS"
    )

    buscar = st.text_input(
        "Buscar cotización",
        placeholder=(
            "Número, cliente o RUC"
        ),
        key="buscar_historial",
    )

    cotizaciones = buscar_cotizaciones(
        buscar
    )

    if not cotizaciones:

        st.info(
            "No existen cotizaciones registradas."
        )

    else:

        st.write(
            f"**Cotizaciones encontradas: "
            f"{len(cotizaciones)}**"
        )

        cotizaciones_ordenadas = sorted(
            cotizaciones,
            key=lambda x: x.get(
                "fecha_registro",
                "",
            ),
            reverse=True,
        )

        for indice, cotizacion in enumerate(
            cotizaciones_ordenadas
        ):

            numero_hist = str(
                cotizacion.get(
                    "numero",
                    "",
                )
            )

            cliente_hist = str(
                cotizacion.get(
                    "cliente",
                    "",
                )
            )

            fecha_hist = str(
                cotizacion.get(
                    "fecha",
                    "",
                )
            )

            subtotal_hist = float(
                cotizacion.get(
                    "subtotal",
                    0,
                )
            )

            descuento_hist = float(
                cotizacion.get(
                    "descuento",
                    0,
                )
            )

            base_hist = max(
                subtotal_hist
                - descuento_hist,
                0,
            )

            aplica_iva_hist = cotizacion.get(
                "aplica_iva",
                True,
            )

            iva_hist = (
                base_hist * 0.15
                if aplica_iva_hist
                else 0
            )

            total_hist = (
                base_hist
                + iva_hist
            )

            cliente_para_titulo = (
                cliente_hist
                if cliente_hist
                else "SIN CLIENTE"
            )

            titulo = (
                f"{numero_hist}"
                f"  |  "
                f"{cliente_para_titulo}"
                f"  |  "
                f"${total_hist:.2f}"
            )

            with st.expander(
                titulo,
                expanded=False,
            ):

                st.write(
                    f"**Fecha:** "
                    f"{fecha_hist}"
                )

                st.write(
                    f"**Cliente:** "
                    f"{cliente_hist}"
                )

                st.write(
                    f"**RUC/CI:** "
                    f"{cotizacion.get('ruc', '')}"
                )

                st.write(
                    f"**Dirección:** "
                    f"{cotizacion.get('direccion', '')}"
                )

                st.write(
                    f"**Teléfono:** "
                    f"{cotizacion.get('telefono', '')}"
                )

                st.write(
                    f"**Correo:** "
                    f"{cotizacion.get('correo', '')}"
                )

                st.markdown(
                    "#### ÍTEMS"
                )

                items_hist = cotizacion.get(
                    "items",
                    [],
                )

                if not items_hist:

                    st.info(
                        "Esta cotización no tiene ítems."
                    )

                else:

                    for numero_item, item in enumerate(
                        items_hist,
                        start=1,
                    ):

                        cantidad_item = float(
                            item.get(
                                "cantidad",
                                0,
                            )
                        )

                        precio_item = float(
                            item.get(
                                "precio",
                                0,
                            )
                        )

                        subtotal_item = (
                            cantidad_item
                            * precio_item
                        )

                        with st.container(
                            border=True
                        ):

                            st.markdown(
                                f"**Ítem "
                                f"{numero_item}: "
                                f"{item.get('descripcion', '')}**"
                            )

                            if item.get(
                                "codigo",
                                "",
                            ):

                                st.write(
                                    f"Código: "
                                    f"{item.get('codigo', '')}"
                                )

                            if item.get(
                                "marca",
                                "",
                            ):

                                st.write(
                                    f"Marca: "
                                    f"{item.get('marca', '')}"
                                )

                            st.write(
                                f"{cantidad_item:.2f} "
                                f"{item.get('unidad', '')} "
                                f"× "
                                f"${precio_item:.2f}"
                            )

                            st.write(
                                f"Subtotal: "
                                f"**${subtotal_item:.2f}**"
                            )

                st.markdown("---")

                st.write(
                    f"Subtotal: "
                    f"**${subtotal_hist:.2f}**"
                )

                st.write(
                    f"Descuento: "
                    f"**${descuento_hist:.2f}**"
                )

                st.write(
                    f"IVA: "
                    f"**${iva_hist:.2f}**"
                )

                st.markdown(
                    f"### TOTAL: "
                    f"${total_hist:.2f}"
                )

                st.markdown(
                    "#### CONDICIONES"
                )

                st.write(
                    f"**Forma de pago:** "
                    f"{cotizacion.get('forma_pago', '')}"
                )

                st.write(
                    f"**Tiempo de entrega:** "
                    f"{cotizacion.get('tiempo_entrega', '')}"
                )

                st.write(
                    f"**Validez:** "
                    f"{cotizacion.get('validez', '')}"
                )

                st.write(
                    f"**Lugar de entrega:** "
                    f"{cotizacion.get('lugar_entrega', '')}"
                )

                st.write(
                    f"**Garantía:** "
                    f"{cotizacion.get('garantia', '')}"
                )

                if cotizacion.get(
                    "observaciones",
                    "",
                ):

                    st.write(
                        f"**Observaciones:** "
                        f"{cotizacion.get('observaciones', '')}"
                    )

                st.markdown("---")

                st.button(
                    "✏️ EDITAR COTIZACIÓN",
                    key=(
                        f"editar_"
                        f"{indice}"
                    ),
                    use_container_width=True,
                    on_click=(
                        cargar_cotizacion_para_editar
                    ),
                    args=(
                        cotizacion,
                    ),
                )

                datos_pdf = dict(
                    cotizacion
                )

                try:

                    datos_pdf[
                        "fecha"
                    ] = datetime.strptime(
                        fecha_hist,
                        "%Y-%m-%d",
                    )

                except Exception:

                    datos_pdf[
                        "fecha"
                    ] = datetime.now()

                try:

                    pdf_historial = generar_pdf_cotizacion(
                        datos_pdf
                    )

                    nombre_pdf = (
                        numero_hist
                        .replace(
                            "/",
                            "-",
                        )
                        .replace(
                            "\\",
                            "-",
                        )
                        .replace(
                            " ",
                            "_",
                        )
                    )

                    st.download_button(
                        label=(
                            "DESCARGAR PDF"
                        ),
                        data=(
                            pdf_historial
                        ),
                        file_name=(
                            f"{nombre_pdf}.pdf"
                        ),
                        mime=(
                            "application/pdf"
                        ),
                        key=(
                            f"pdf_historial_"
                            f"{indice}"
                        ),
                        use_container_width=True,
                    )

                except Exception as error:

                    st.error(
                        f"No se pudo generar "
                        f"el PDF: {error}"
                    )

    st.stop()


# =========================================================
# NUEVA COTIZACIÓN / EDICIÓN
# =========================================================

if st.session_state.get(
    "modo_edicion",
    False,
):

    st.info(
        "✏️ ESTÁS EDITANDO UNA COTIZACIÓN EXISTENTE. "
        "Al generar nuevamente el PDF se actualizará "
        "el historial."
    )


# =========================================================
# DATOS DE LA COTIZACIÓN
# =========================================================

with st.expander(
    "1. DATOS DE LA COTIZACIÓN",
    expanded=True,
):

    numero = st.text_input(
        "Número de cotización",
        placeholder=(
            "Ejemplo: COT-01532"
        ),
        key="numero_cotizacion",
    )

    if "fecha_cotizacion" not in st.session_state:
        st.session_state[
            "fecha_cotizacion"
        ] = datetime.now().date()

    fecha = st.date_input(
        "Fecha",
        key="fecha_cotizacion",
    )


# =========================================================
# DATOS DEL CLIENTE
# =========================================================

with st.expander(
    "2. DATOS DEL CLIENTE",
    expanded=True,
):

    cliente = st.text_input(
        "Cliente o razón social",
        placeholder=(
            "Nombre del cliente"
        ),
        key="cliente",
    )

    ruc = st.text_input(
        "RUC o cédula",
        placeholder=(
            "Número de identificación"
        ),
        key="ruc_cliente",
    )

    direccion = st.text_input(
        "Dirección",
        placeholder=(
            "Dirección del cliente"
        ),
        key="direccion_cliente",
    )

    telefono = st.text_input(
        "Teléfono",
        placeholder=(
            "Teléfono del cliente"
        ),
        key="telefono_cliente",
    )

    correo = st.text_input(
        "Correo",
        placeholder=(
            "correo@ejemplo.com"
        ),
        key="correo_cliente",
    )


# =========================================================
# AGREGAR PRODUCTO
# =========================================================

with st.expander(
    "3. AGREGAR PRODUCTO",
    expanded=True,
):

    with st.form(
        key="formulario_producto",
        clear_on_submit=True,
    ):

        codigo = st.text_input(
            "Código o número de parte",
            placeholder="Opcional",
        )

        descripcion = st.text_area(
            "Descripción",
            placeholder=(
                "Descripción completa "
                "del producto"
            ),
        )

        marca = st.text_input(
            "Marca",
            placeholder="Opcional",
        )

        unidad = st.selectbox(
            "Unidad",
            options=[
                "UND",
                "M",
                "M2",
                "M3",
                "KG",
                "LT",
                "GL",
                "ROLLO",
                "CAJA",
                "KIT",
                "PAR",
                "SERVICIO",
            ],
        )

        cantidad = st.number_input(
            "Cantidad",
            min_value=0.01,
            value=1.00,
            step=1.00,
            format="%.2f",
        )

        precio = st.number_input(
            "Precio unitario",
            min_value=0.00,
            value=0.00,
            step=0.01,
            format="%.2f",
        )

        agregar = st.form_submit_button(
            "AGREGAR ÍTEM",
            type="primary",
            use_container_width=True,
        )

    if agregar:

        if not descripcion.strip():

            st.error(
                "La descripción del producto "
                "es obligatoria."
            )

        elif cantidad <= 0:

            st.error(
                "La cantidad debe ser "
                "mayor que cero."
            )

        elif precio < 0:

            st.error(
                "El precio no puede "
                "ser negativo."
            )

        else:

            st.session_state[
                "items_cotizacion"
            ].append(
                {
                    "codigo":
                        codigo.strip(),

                    "descripcion":
                        descripcion.strip(),

                    "marca":
                        marca.strip(),

                    "unidad":
                        unidad,

                    "cantidad":
                        float(cantidad),

                    "precio":
                        float(precio),
                }
            )

            st.success(
                "Ítem agregado correctamente."
            )

            st.rerun()


# =========================================================
# LISTADO DE ÍTEMS
# =========================================================

st.subheader(
    "ÍTEMS DE LA COTIZACIÓN"
)

if not st.session_state[
    "items_cotizacion"
]:

    st.info(
        "Todavía no has agregado productos."
    )

else:

    for indice, item in enumerate(
        st.session_state[
            "items_cotizacion"
        ]
    ):

        subtotal_item = (
            float(
                item["cantidad"]
            )
            *
            float(
                item["precio"]
            )
        )

        with st.container(
            border=True
        ):

            st.markdown(
                f"**Ítem "
                f"{indice + 1}: "
                f"{item['descripcion']}**"
            )

            if item.get(
                "codigo"
            ):

                st.write(
                    f"Código: "
                    f"{item['codigo']}"
                )

            if item.get(
                "marca"
            ):

                st.write(
                    f"Marca: "
                    f"{item['marca']}"
                )

            st.write(
                f"{item['cantidad']:.2f} "
                f"{item['unidad']} "
                f"× "
                f"${item['precio']:.2f}"
            )

            st.write(
                f"Subtotal: "
                f"**${subtotal_item:.2f}**"
            )

            if st.button(
                "ELIMINAR",
                key=(
                    f"eliminar_item_"
                    f"{indice}"
                ),
                use_container_width=True,
            ):

                st.session_state[
                    "items_cotizacion"
                ].pop(
                    indice
                )

                st.rerun()


# =========================================================
# CÁLCULO DEL SUBTOTAL
# =========================================================

subtotal = sum(
    float(
        item["cantidad"]
    )
    *
    float(
        item["precio"]
    )
    for item
    in st.session_state[
        "items_cotizacion"
    ]
)


# =========================================================
# TOTALES Y CONDICIONES
# =========================================================

with st.expander(
    "4. TOTALES Y CONDICIONES",
    expanded=True,
):

    descuento = st.number_input(
        "Descuento total",
        min_value=0.00,
        value=0.00,
        step=0.01,
        format="%.2f",
        key="descuento_total",
    )

    aplica_iva = st.checkbox(
        "Aplicar IVA 15%",
        value=True,
        key="aplica_iva",
    )

    base_iva = max(
        subtotal
        - descuento,
        0,
    )

    iva = (
        base_iva * 0.15
        if aplica_iva
        else 0
    )

    total = (
        base_iva
        + iva
    )

    st.markdown("---")

    st.write(
        f"Subtotal: "
        f"**${subtotal:.2f}**"
    )

    st.write(
        f"Descuento: "
        f"**${descuento:.2f}**"
    )

    st.write(
        f"IVA: "
        f"**${iva:.2f}**"
    )

    st.markdown(
        f"### TOTAL: "
        f"${total:.2f}"
    )

    st.markdown("---")

    forma_pago = st.selectbox(
        "Forma de pago",
        options=[
            "CONTADO",
            "CRÉDITO 15 DÍAS",
            "CRÉDITO 30 DÍAS",
            "CRÉDITO 45 DÍAS",
            "CRÉDITO 60 DÍAS",
            "POR DEFINIR",
        ],
        key="forma_pago",
    )

    tiempo_entrega = st.text_input(
        "Tiempo de entrega",
        value="ENTREGA INMEDIATA",
        key="tiempo_entrega",
    )

    validez = st.text_input(
        "Validez de la oferta",
        value="7 DÍAS",
        key="validez_oferta",
    )

    lugar_entrega = st.text_input(
        "Lugar de entrega",
        value="QUITO",
        key="lugar_entrega",
    )

    garantia = st.text_input(
        "Garantía",
        value="SEGÚN FABRICANTE",
        key="garantia",
    )

    observaciones = st.text_area(
        "Observaciones",
        placeholder="Opcional",
        key="observaciones",
    )


st.markdown("---")


# =========================================================
# GENERAR O ACTUALIZAR PDF
# =========================================================

if st.session_state.get(
    "modo_edicion",
    False,
):

    texto_boton_generar = (
        "ACTUALIZAR COTIZACIÓN "
        "Y GENERAR PDF"
    )

else:

    texto_boton_generar = (
        "GENERAR COTIZACIÓN PDF"
    )


generar = st.button(
    texto_boton_generar,
    type="primary",
    key="boton_generar_pdf",
    use_container_width=True,
)


if generar:

    errores = []

    if not numero.strip():

        errores.append(
            "Ingresa el número "
            "de cotización."
        )

    if not cliente.strip():

        errores.append(
            "Ingresa el nombre "
            "del cliente."
        )

    if not st.session_state[
        "items_cotizacion"
    ]:

        errores.append(
            "Agrega al menos "
            "un producto."
        )

    if descuento > subtotal:

        errores.append(
            "El descuento no puede "
            "ser mayor que el subtotal."
        )

    if errores:

        for error in errores:

            st.error(
                error
            )

    else:

        datos = {

            "numero":
                numero.strip(),

            "fecha":
                datetime.combine(
                    fecha,
                    datetime.min.time(),
                ),

            "cliente":
                cliente.strip(),

            "ruc":
                ruc.strip(),

            "direccion":
                direccion.strip(),

            "telefono":
                telefono.strip(),

            "correo":
                correo.strip(),

            "items":
                st.session_state[
                    "items_cotizacion"
                ],

            "subtotal":
                subtotal,

            "descuento":
                descuento,

            "aplica_iva":
                aplica_iva,

            "forma_pago":
                forma_pago,

            "tiempo_entrega":
                tiempo_entrega.strip(),

            "validez":
                validez.strip(),

            "lugar_entrega":
                lugar_entrega.strip(),

            "garantia":
                garantia.strip(),

            "observaciones":
                observaciones.strip(),
        }

        try:

            pdf = generar_pdf_cotizacion(
                datos
            )

            if st.session_state.get(
                "modo_edicion",
                False,
            ):

                numero_original = str(
                    st.session_state.get(
                        "numero_original_edicion",
                        "",
                    )
                ).strip()

                numero_nuevo = numero.strip()

                if (
                    numero_original
                    and
                    numero_original
                    != numero_nuevo
                ):

                    eliminar_cotizacion(
                        numero_original
                    )

            guardar_cotizacion(
                datos
            )

            nombre_archivo = (
                numero.strip()
                .replace(
                    "/",
                    "-",
                )
                .replace(
                    "\\",
                    "-",
                )
                .replace(
                    " ",
                    "_",
                )
            )

            if st.session_state.get(
                "modo_edicion",
                False,
            ):

                st.success(
                    "Cotización actualizada "
                    "correctamente."
                )

                st.session_state[
                    "numero_original_edicion"
                ] = numero.strip()

            else:

                st.success(
                    "Cotización generada "
                    "y guardada correctamente."
                )

            st.download_button(
                label="DESCARGAR PDF",
                data=pdf,
                file_name=(
                    f"{nombre_archivo}.pdf"
                ),
                mime=(
                    "application/pdf"
                ),
                key="descargar_pdf",
                use_container_width=True,
            )

        except Exception as error:

            st.error(
                f"No se pudo generar "
                f"el PDF: {error}"
            )


# =========================================================
# LIMPIAR / NUEVA COTIZACIÓN
# =========================================================

if st.button(
    "LIMPIAR / NUEVA COTIZACIÓN",
    key="boton_nueva_cotizacion",
    use_container_width=True,
):

    claves_a_eliminar = [

        "items_cotizacion",

        "numero_cotizacion",

        "fecha_cotizacion",

        "cliente",

        "ruc_cliente",

        "direccion_cliente",

        "telefono_cliente",

        "correo_cliente",

        "descuento_total",

        "aplica_iva",

        "forma_pago",

        "tiempo_entrega",

        "validez_oferta",

        "lugar_entrega",

        "garantia",

        "observaciones",

        "modo_edicion",

        "numero_original_edicion",
    ]

    for clave in claves_a_eliminar:

        if clave in st.session_state:

            del st.session_state[
                clave
            ]

    st.session_state[
        "fecha_cotizacion"
    ] = datetime.now().date()

    st.rerun()