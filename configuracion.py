import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EMPRESA = {
    "nombre": "ELECTROLINKEC S.A.S.",
    "ruc": "1793227468001",
    "subtitulo": "Material eléctrico, redes y telecomunicaciones",
    "direccion": "Quito - Ecuador - Calle N89 - Pasaje E2B",
    "telefono": "+593 98 758 9412",
    "email": "ventasn@electrolinkec.com",
    "logo_path": os.path.join(BASE_DIR, "recursos", "logo.png"),
}

MONEDA = "USD"
IVA_PORCENTAJE = 0.15

COLORES = {
    "azul": "#004FAF",
    "naranja": "#FFBD59",
    "gris": "#6D6D6E",
    "gris_claro": "#F2F4F8",
    "blanco": "#FFFFFF",
}