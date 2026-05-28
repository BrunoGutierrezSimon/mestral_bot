# api.py — Peticiones a las APIs de Open-Meteo

import requests
from utils import ms_to_knots, get_wind_direction, estado_mar, color_viento

# Convierte el nombre de una ciudad en coordenadas (latitud y longitud)
# El usuario escribe "Tarragona" → la API devuelve las coordenadas
def get_coordinates(city):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=es"
    data = requests.get(url).json()
    if "results" not in data:
        return None
    r = data["results"][0]
    return r["latitude"], r["longitude"], r["name"]

# Pide los datos meteorológicos a Open-Meteo
# Devuelve temperatura, viento, rachas, lluvia... de los próximos 7 días
def get_weather(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,precipitation_probability,"
        f"windspeed_10m,windgusts_10m,winddirection_10m"
        f"&daily=temperature_2m_max,temperature_2m_min,"
        f"precipitation_probability_max,windspeed_10m_max,"
        f"windgusts_10m_max,winddirection_10m_dominant"
        f"&wind_speed_unit=ms&timezone=Europe/Madrid&forecast_days=7"
    )
    return requests.get(url).json()

# Pide los datos marinos a Open-Meteo (API separada de la meteorológica)
# Devuelve altura de olas y dirección del oleaje
def get_marine(lat, lon):
    url = (
        f"https://marine-api.open-meteo.com/v1/marine?"
        f"latitude={lat}&longitude={lon}"
        f"&current=wave_height,wave_direction"
        f"&daily=wave_height_max"
        f"&timezone=Europe/Madrid&forecast_days=7"
    )
    return requests.get(url).json()

# Construye el mensaje completo de previsión náutica
# Usado tanto por /tiempo como por el parte diario automático
def construir_mensaje(name, weather, marine):
    from datetime import datetime

    # Datos actuales
    c = weather["current"]
    wind_knots = ms_to_knots(c["windspeed_10m"])
    gusts_knots = ms_to_knots(c["windgusts_10m"])
    wind_dir = get_wind_direction(c["winddirection_10m"])

    wave_str = "N/A"
    if "current" in marine and "wave_height" in marine["current"]:
        wave_now = marine["current"]["wave_height"]
        # Comprobamos que wave_now no sea None antes de usarlo
        if wave_now is not None:
            wave_str = f"{wave_now}m ({estado_mar(wave_now)})"

    msg = f"🌬️ *Mestral — {name}*\n\n"
    msg += f"*Ahora mismo:*\n"
    msg += f"🌡️ Temperatura: {c['temperature_2m']}°C\n"
    msg += f"💨 Viento: {wind_knots}kt {wind_dir} | Rachas: {gusts_knots}kt\n"
    msg += f"🌧️ Prob. lluvia: {c['precipitation_probability']}%\n"
    msg += f"🌊 Olas: {wave_str}\n"

    # Previsión semanal
    msg += f"\n*Previsión 7 días:*\n"
    daily = weather["daily"]
    marine_daily = marine.get("daily", {})

    for i in range(7):
        fecha = daily["time"][i]
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
        dias = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
        dia_nombre = dias[fecha_obj.weekday()]
        dia_formato = f"{dia_nombre} {fecha_obj.strftime('%d/%m')}"

        viento = ms_to_knots(daily["windspeed_10m_max"][i])
        rachas = ms_to_knots(daily["windgusts_10m_max"][i])
        direccion = get_wind_direction(daily["winddirection_10m_dominant"][i])
        lluvia = daily["precipitation_probability_max"][i]

        if "wave_height_max" in marine_daily and marine_daily["wave_height_max"][i]:
            olas = marine_daily["wave_height_max"][i]
            olas_str = f"{olas}m ({estado_mar(olas)})"
        else:
            olas_str = "N/A"

        color = color_viento(viento)
        msg += f"{color} {dia_formato}: Viento {viento}kt {direccion} | Rachas {rachas}kt | 🌊{olas_str} | 🌧️{lluvia}%\n"

    return msg