# handlers.py — Comandos del bot

import pytz
from datetime import time, datetime
from telegram import Update
from telegram.ext import ContextTypes
from api import get_coordinates, get_weather, get_marine, construir_mensaje

# Comando /start → mensaje de bienvenida
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⛵ *Bienvenido a Mestral!*\n\n"
        "Usa /tiempo <ciudad> para ver la previsión náutica.\n"
        "Usa /activar <ciudad> para recibir el parte cada mañana a las 8:00.\n"
        "Usa /desactivar para cancelar el parte diario.\n\n"
        "Ejemplo: /tiempo Tarragona",
        parse_mode="Markdown"
    )

# Comando /tiempo <ciudad> → previsión náutica completa
async def tiempo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Escribe una ciudad. Ejemplo: /tiempo Tarragona")
        return

    city = " ".join(context.args)
    coords = get_coordinates(city)

    if not coords:
        await update.message.reply_text(f"❌ No he encontrado '{city}'. Prueba con otra ciudad.")
        return

    lat, lon, name = coords
    weather = get_weather(lat, lon)
    marine = get_marine(lat, lon)
    msg = construir_mensaje(name, weather, marine)

    await update.message.reply_text(msg, parse_mode="Markdown")

# Función que ejecuta el parte diario automáticamente cada día a las 8:00
async def parte_diario(context: ContextTypes.DEFAULT_TYPE):
    ciudad = context.job.data["ciudad"]
    chat_id = context.job.data["chat_id"]

    coords = get_coordinates(ciudad)
    if not coords:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ No encuentro '{ciudad}'.")
        return

    lat, lon, name = coords
    weather = get_weather(lat, lon)
    marine = get_marine(lat, lon)
    msg = construir_mensaje(name, weather, marine)

    await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")

# Comando /activar <ciudad> → activa el parte diario a las 8:00
async def activar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Escribe una ciudad. Ejemplo: /activar Tarragona")
        return

    ciudad = " ".join(context.args)
    chat_id = update.message.chat_id

    # Cancelamos el job anterior si ya había uno activo para este usuario
    jobs_actuales = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in jobs_actuales:
        job.schedule_removal()

    # Programamos el mensaje diario a las 8:00 hora de Madrid
    hora = time(8, 0, tzinfo=pytz.timezone("Europe/Madrid"))
    context.job_queue.run_daily(
        parte_diario,
        time=hora,
        name=str(chat_id),
        data={"ciudad": ciudad, "chat_id": chat_id}
    )

    await update.message.reply_text(
        f"✅ Parte diario activado para *{ciudad}* a las 8:00\n"
        f"Usa /desactivar para cancelarlo.",
        parse_mode="Markdown"
    )

# Comando /desactivar → cancela el parte diario
async def desactivar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    jobs_actuales = context.job_queue.get_jobs_by_name(str(chat_id))

    if not jobs_actuales:
        await update.message.reply_text("⚠️ No tienes ningún parte diario activo.")
        return

    for job in jobs_actuales:
        job.schedule_removal()

    await update.message.reply_text("❌ Parte diario desactivado.")