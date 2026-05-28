# parte_diario.py — Script que ejecuta GitHub Actions cada día a las 8:00
# No necesita escucha activa, simplemente manda el parte y se cierra

import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot
from api import get_coordinates, get_weather, get_marine, construir_mensaje

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Tu chat_id personal — a quién le manda el parte
CHAT_ID = int(os.getenv("CHAT_ID"))

# Ciudad por defecto para el parte diario
CIUDAD = "L'Hospitalet de l'Infant"

async def enviar_parte():
    bot = Bot(token=TOKEN)
    
    coords = get_coordinates(CIUDAD)
    if not coords:
        await bot.send_message(chat_id=CHAT_ID, text=f"❌ No encuentro '{CIUDAD}'.")
        return

    lat, lon, name = coords
    weather = get_weather(lat, lon)
    marine = get_marine(lat, lon)
    msg = construir_mensaje(name, weather, marine)

    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")
    print("Parte enviado correctamente ✅")

if __name__ == "__main__":
    asyncio.run(enviar_parte())