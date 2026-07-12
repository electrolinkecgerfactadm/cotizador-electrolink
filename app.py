from datetime import datetime

import streamlit as st

from generador_pdf import generar_pdf_cotizacion


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
        max-width: 900px;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    .titulo-principal {
        color: #004FAF;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .subtitulo {
        color: #6D6D6E;
        margin-bottom: 1rem;
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
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ESTADO DE LA APLICACIÓN
# =========================================================

if "items_cotizacion" not in st.session_state:
    st.session_state["items_cotizacion"] = []


# =========================================================
# ENCABEZADO
# =========================================================

st.markdown(
    '<div class="titulo-principal">COTIZADOR ELECTROLINK</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitulo">'
    'Generación rápida de cotizaciones en PDF'
    '</div>',
    unsafe_allow_html=True,
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
        placeholder="Ejemplo: COT-01532",
        key="numero_cotizacion",
    )

    fecha = st.date_input(
        "Fecha",
        value=datetime.now().date(),
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
        placeholder="Nombre del cliente",
        key="cliente",
    )

    ruc = st.text_input(
        "RUC o cédula",
        placeholder="Número de identificación",
        key="ruc_cliente",
    )

    direccion = st.text_input(
        "Dirección",
        placeholder="Dirección del cliente",
        key="direccion_cliente",
    )

    telefono = st.text_input(
        "Teléfono",
        placeholder="Teléfono del cliente",
        key="telefono_cliente",
    )

    correo = st.text_input(
        "Correo",
        placeholder="correo@ejemplo.com",
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
            placeholder="Descripción completa del producto",
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
                "La descripción del producto es obligatoria."
            )

        elif cantidad <= 0:
            st.error(
                "La cantidad debe ser mayor que cero."
            )

        elif precio < 0:
            st.error(
                "El precio no puede ser negativo."
            )

        else:
            st.session_state["items_cotizacion"].append(
                {
                    "codigo": codigo.strip(),
                    "descripcion": descripcion.strip(),
                    "marca": marca.strip(),
                    "unidad": unidad,
                    "cantidad": float(cantidad),
                    "precio": float(precio),
                }
            )

            st.success(
                "Ítem agregado correctamente."
            )

            st.rerun()


# =========================================================
# LISTADO DE ÍTEMS
# =========================================================

st.subheader("ÍTEMS DE LA COTIZACIÓN")

if not st.session_state["items_cotizacion"]:
    st.info(
        "Todavía no has agregado productos."
    )

else:
    for indice, item in enumerate(
        st.session_state["items_cotizacion"]
    ):
        subtotal_item = (
            float(item["cantidad"])
            * float(item["precio"])
        )

        with st.container(border=True):
            st.markdown(
                f"**Ítem {indice + 1}: "
                f"{item['descripcion']}**"
            )

            if item.get("codigo"):
                st.write(
                    f"Código: {item['codigo']}"
                )

            if item.get("marca"):
                st.write(
                    f"Marca: {item['marca']}"
                )

            st.write(
                f"{item['cantidad']:.2f} "
                f"{item['unidad']} × "
                f"${item['precio']:.2f}"
            )

            st.write(
                f"Subtotal: "
                f"**${subtotal_item:.2f}**"
            )

            if st.button(
                "ELIMINAR",
                key=f"eliminar_item_{indice}",
                use_container_width=True,
            ):
                st.session_state[
                    "items_cotizacion"
                ].pop(indice)

                st.rerun()


# =========================================================
# CÁLCULO DEL SUBTOTAL
# =========================================================

subtotal = sum(
    float(item["cantidad"])
    * float(item["precio"])
    for item in st.session_state["items_cotizacion"]
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
        subtotal - descuento,
        0,
    )

    iva = (
        base_iva * 0.15
        if aplica_iva
        else 0
    )

    total = base_iva + iva

    st.markdown("---")

    st.write(
        f"Subtotal: **${subtotal:.2f}**"
    )

    st.write(
        f"Descuento: **${descuento:.2f}**"
    )

    st.write(
        f"IVA: **${iva:.2f}**"
    )

    st.write(
        f"TOTAL: **${total:.2f}**"
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
# GENERAR PDF
# =========================================================

generar = st.button(
    "GENERAR COTIZACIÓN PDF",
    type="primary",
    key="boton_generar_pdf",
    use_container_width=True,
)


if generar:
    errores = []

    if not numero.strip():
        errores.append(
            "Ingresa el número de cotización."
        )

    if not cliente.strip():
        errores.append(
            "Ingresa el nombre del cliente."
        )

    if not st.session_state["items_cotizacion"]:
        errores.append(
            "Agrega al menos un producto."
        )

    if descuento > subtotal:
        errores.append(
            "El descuento no puede ser mayor "
            "que el subtotal."
        )

    if errores:
        for error in errores:
            st.error(error)

    else:
        datos = {
            "numero": numero.strip(),
            "fecha": datetime.combine(
                fecha,
                datetime.min.time(),
            ),
            "cliente": cliente.strip(),
            "ruc": ruc.strip(),
            "direccion": direccion.strip(),
            "telefono": telefono.strip(),
            "correo": correo.strip(),
            "items": st.session_state[
                "items_cotizacion"
            ],
            "subtotal": subtotal,
            "descuento": descuento,
            "aplica_iva": aplica_iva,
            "forma_pago": forma_pago,
            "tiempo_entrega": (
                tiempo_entrega.strip()
            ),
            "validez": validez.strip(),
            "lugar_entrega": (
                lugar_entrega.strip()
            ),
            "garantia": garantia.strip(),
            "observaciones": (
                observaciones.strip()
            ),
        }

        try:
            pdf = generar_pdf_cotizacion(
                datos
            )

            nombre_archivo = (
                numero.strip()
                .replace("/", "-")
                .replace("\\", "-")
                .replace(" ", "_")
            )

            st.success(
                "Cotización generada correctamente."
            )

            st.download_button(
                label="DESCARGAR PDF",
                data=pdf,
                file_name=(
                    f"{nombre_archivo}.pdf"
                ),
                mime="application/pdf",
                key="descargar_pdf",
                use_container_width=True,
            )

        except Exception as error:
            st.error(
                f"No se pudo generar el PDF: "
                f"{error}"
            )


# =========================================================
# NUEVA COTIZACIÓN
# =========================================================

if st.button(
    "NUEVA COTIZACIÓN",
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
    ]

    for clave in claves_a_eliminar:
        if clave in st.session_state:
            del st.session_state[clave]

    st.rerun()