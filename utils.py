# utils.py — Funciones de conversión y utilidades

# Convierte metros por segundo a nudos (unidad náutica de velocidad)
# 1 m/s = 1.944 nudos
def ms_to_knots(ms):
    return round(ms * 1.944, 1)

# Convierte grados (0-360) a nombre mediterráneo + dirección cardinal
# Cada sector ocupa 45 grados en la rosa de los vientos
def get_wind_direction(degrees):
    directions = [
        "Tramuntana (N)", "Gregal (NE)", "Llevant (E)", "Xaloc (SE)",
        "Migjorn (S)", "Llebeig (SO)", "Ponent (O)", "Mestral (NO)"
    ]
    return directions[round(degrees / 45) % 8]

# Convierte la altura de olas en término náutico oficial
def estado_mar(metros):
    if metros < 0.5:
        return "Llana"
    elif metros < 1.5:
        return "Rizada"
    elif metros < 2.5:
        return "Marejada"
    else:
        return "Fuerte marejada"

# Devuelve dos círculos de color según la velocidad del viento en nudos
# Escala inspirada en Windfinder
def color_viento(nudos):
    if nudos < 5:
        return "🟢🟢"
    elif nudos < 10:
        return "🟢🔵"
    elif nudos < 15:
        return "🔵🔵"
    elif nudos < 20:
        return "🔵🟡"
    elif nudos < 25:
        return "🟡🟡"
    elif nudos < 30:
        return "🟡🔴"
    elif nudos < 35:
        return "🔴🔴"
    else:
        return "🔴🔴"