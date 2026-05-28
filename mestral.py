# mestral.py — Arranque del bot

import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler
from handlers import start, tiempo, activar, desactivar

# Cargamos el token del archivo .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # Registramos todos los comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tiempo", tiempo))
    app.add_handler(CommandHandler("activar", activar))
    app.add_handler(CommandHandler("desactivar", desactivar))

    print("Mestral en marcha! 🌬️")
    app.run_polling()