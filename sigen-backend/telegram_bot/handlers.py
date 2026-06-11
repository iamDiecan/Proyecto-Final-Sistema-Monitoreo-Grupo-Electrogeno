import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timedelta

from telegram_bot.plotter import generate_trend_plot

logger = logging.getLogger(__name__)

# Memoria temporal para silenciar alertas
MUTED_UNTIL = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador del comando /start"""
    user = update.effective_user
    text = (
        f"⚡ *Bienvenido a SIGEGEN-alert* ⚡\n\n"
        f"Hola {user.first_name}, soy el bot oficial de monitoreo industrial de SIGEGEN.\n"
        f"Aquí puedes monitorear en tiempo real los grupos electrógenos.\n\n"
        f"Comandos disponibles:\n"
        f"📊 /estado - Resumen de parámetros\n"
        f"📈 /grafico [parametro] - Generar gráfico\n"
        f"⚙️ /alertas - Configurar umbrales\n"
        f"📜 /historial - Últimos registros (24h)\n"
        f"🔕 /silenciar [horas] - Silenciar alertas\n"
    )
    
    keyboard = [
        [InlineKeyboardButton("📊 Ver Estado", callback_data="cmd_estado")],
        [InlineKeyboardButton("📈 Gráfico de Tensión", callback_data="cmd_grafico_tension")],
        [InlineKeyboardButton("🔕 Silenciar 1h", callback_data="cmd_silenciar_1h")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def estado_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador del comando /estado"""
    # En un escenario real, consultar a la DB. Usamos mock de parámetros por simplicidad.
    text = (
        "⚡ *Estado Actual: Nodo 01 - Capital* ⚡\n\n"
        "🟢 *Tensión*: 220 V (Normal: 210-230)\n"
        "🟢 *Corriente*: 350 A (Normal: 0-500)\n"
        "🟢 *Frecuencia*: 60.1 Hz (Normal: 59-61)\n"
        "🟢 *Temperatura*: 85 °C (Normal: 70-95)\n"
        "🟢 *Presión Aceite*: 5.5 bar (Normal: 3-7)\n"
        "🟢 *Combustible*: 85 % (Normal: >20)\n\n"
        "Status Global: ÓPTIMO 🟢"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def alertas_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador del comando /alertas"""
    text = (
        "⚙️ *Configuración de Umbrales* ⚙️\n\n"
        "Actualmente los umbrales están definidos por el sistema experto. "
        "Para modificarlos, usa el panel web (http://localhost:3000/configuracion) o "
        "envía el comando:\n\n`/set_umbral [parametro] [min] [max]`\n\n"
        "Ejemplo: `/set_umbral tension 200 240`"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def historial_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador del comando /historial"""
    text = (
        "📜 *Últimas alertas (24h)*\n\n"
        "• 10:15 - Nivel de Combustible bajó al 40% [🟡 Advertencia]\n"
        "• 08:30 - Pico de Tensión 245V detectado [🔴 Crítico]\n"
        "• 08:35 - Tensión estabilizada en 225V [🟢 Normal]"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def grafico_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador del comando /grafico"""
    args = context.args
    param = args[0] if args else "tension"
    
    await update.message.reply_text("Generando gráfico, por favor espera... ⏳")
    
    # Mock data para el gráfico
    import random
    data = []
    base_val = 220 if param.lower() == "tension" else 60
    for i in range(24):
        data.append({"timestamp": f"2026-06-10T{i:02d}:00:00", "value": base_val + random.uniform(-5, 5)})
        
    image_bytes = generate_trend_plot(param, data)
    
    if image_bytes:
        await update.message.reply_photo(photo=image_bytes, caption=f"Gráfico de tendencia de 24h para: {param.upper()}")
    else:
        await update.message.reply_text("No hay datos suficientes para generar el gráfico.")

async def silenciar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador del comando /silenciar"""
    chat_id = update.effective_chat.id
    args = context.args
    horas = int(args[0]) if args and args[0].isdigit() else 1
    
    muted_until = datetime.now() + timedelta(hours=horas)
    MUTED_UNTIL[chat_id] = muted_until
    
    await update.message.reply_text(f"🔕 Las alertas push han sido silenciadas por {horas} hora(s) (hasta las {muted_until.strftime('%H:%M')}).")

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador para botones inline"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cmd_estado":
        await estado_command(update, context)
    elif query.data == "cmd_grafico_tension":
        context.args = ["tension"]
        await grafico_command(update, context)
    elif query.data == "cmd_silenciar_1h":
        context.args = ["1"]
        await silenciar_command(update, context)
