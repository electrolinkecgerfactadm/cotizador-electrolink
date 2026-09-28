import json
import os
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(
    BASE_DIR,
    "datos",
)

ARCHIVO_COTIZACIONES = os.path.join(
    DATA_DIR,
    "cotizaciones.json",
)


def asegurar_archivo():
    os.makedirs(
        DATA_DIR,
        exist_ok=True,
    )

    if not os.path.exists(
        ARCHIVO_COTIZACIONES
    ):
        with open(
            ARCHIVO_COTIZACIONES,
            "w",
            encoding="utf-8",
        ) as archivo:
            json.dump(
                [],
                archivo,
                ensure_ascii=False,
                indent=4,
            )


def cargar_cotizaciones():
    asegurar_archivo()

    try:
        with open(
            ARCHIVO_COTIZACIONES,
            "r",
            encoding="utf-8",
        ) as archivo:
            datos = json.load(
                archivo
            )

            if isinstance(
                datos,
                list,
            ):
                return datos

            return []

    except (
        json.JSONDecodeError,
        FileNotFoundError,
    ):
        return []


def guardar_lista_cotizaciones(
    cotizaciones
):
    asegurar_archivo()

    with open(
        ARCHIVO_COTIZACIONES,
        "w",
        encoding="utf-8",
    ) as archivo:
        json.dump(
            cotizaciones,
            archivo,
            ensure_ascii=False,
            indent=4,
        )


def guardar_cotizacion(
    datos
):
    cotizaciones = (
        cargar_cotizaciones()
    )

    fecha = datos.get(
        "fecha"
    )

    if isinstance(
        fecha,
        datetime,
    ):
        fecha_texto = (
            fecha.strftime(
                "%Y-%m-%d"
            )
        )
    else:
        fecha_texto = str(
            fecha or ""
        )

    registro = {
        "numero": datos.get(
            "numero",
            "",
        ),
        "fecha": fecha_texto,
        "cliente": datos.get(
            "cliente",
            "",
        ),
        "ruc": datos.get(
            "ruc",
            "",
        ),
        "direccion": datos.get(
            "direccion",
            "",
        ),
        "telefono": datos.get(
            "telefono",
            "",
        ),
        "correo": datos.get(
            "correo",
            "",
        ),
        "items": datos.get(
            "items",
            [],
        ),
        "subtotal": float(
            datos.get(
                "subtotal",
                0,
            )
        ),
        "descuento": float(
            datos.get(
                "descuento",
                0,
            )
        ),
        "aplica_iva": bool(
            datos.get(
                "aplica_iva",
                True,
            )
        ),
        "forma_pago": datos.get(
            "forma_pago",
            "",
        ),
        "tiempo_entrega": datos.get(
            "tiempo_entrega",
            "",
        ),
        "validez": datos.get(
            "validez",
            "",
        ),
        "lugar_entrega": datos.get(
            "lugar_entrega",
            "",
        ),
        "garantia": datos.get(
            "garantia",
            "",
        ),
        "observaciones": datos.get(
            "observaciones",
            "",
        ),
        "fecha_registro": (
            datetime.now()
            .isoformat(
                timespec="seconds"
            )
        ),
    }

    # Si ya existe el mismo número,
    # reemplazamos esa cotización.
    reemplazada = False

    for indice, cotizacion in enumerate(
        cotizaciones
    ):
        if str(
            cotizacion.get(
                "numero",
                "",
            )
        ).strip() == str(
            registro["numero"]
        ).strip():
            cotizaciones[
                indice
            ] = registro

            reemplazada = True

            break

    if not reemplazada:
        cotizaciones.append(
            registro
        )

    guardar_lista_cotizaciones(
        cotizaciones
    )

    return registro


def buscar_cotizaciones(
    texto=""
):
    cotizaciones = (
        cargar_cotizaciones()
    )

    texto = str(
        texto or ""
    ).strip().lower()

    if not texto:
        return cotizaciones

    resultado = []

    for cotizacion in cotizaciones:
        contenido = (
            f"{cotizacion.get('numero', '')} "
            f"{cotizacion.get('fecha', '')} "
            f"{cotizacion.get('cliente', '')} "
            f"{cotizacion.get('ruc', '')}"
        ).lower()

        if texto in contenido:
            resultado.append(
                cotizacion
            )

    return resultado


def obtener_cotizacion(
    numero
):
    numero = str(
        numero or ""
    ).strip()

    for cotizacion in (
        cargar_cotizaciones()
    ):
        if str(
            cotizacion.get(
                "numero",
                "",
            )
        ).strip() == numero:
            return cotizacion

    return None


def eliminar_cotizacion(
    numero
):
    numero = str(
        numero or ""
    ).strip()

    cotizaciones = (
        cargar_cotizaciones()
    )

    nuevas = [
        cotizacion
        for cotizacion
        in cotizaciones
        if str(
            cotizacion.get(
                "numero",
                "",
            )
        ).strip()
        != numero
    ]

    guardar_lista_cotizaciones(
        nuevas
    )

    return (
        len(nuevas)
        < len(cotizaciones)
    )