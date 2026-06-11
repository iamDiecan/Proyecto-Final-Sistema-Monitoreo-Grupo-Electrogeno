import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import get_settings

from telegram_bot.handlers import (
    start_command, estado_command, alertas_command, 
    historial_command, grafico_command, silenciar_command,
    callback_query_handler, MUTED_UNTIL
)
from datetime import datetime

logger = logging.getLogger(__name__)

bot_app = None

async def init_telegram_bot():
    """Inicializa la aplicación del bot de Telegram."""
    global bot_app
    settings = get_settings()
    token = settings.telegram_bot_token
    
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN no configurado. El bot no iniciará.")
        return None
        
    bot_app = ApplicationBuilder().token(token).build()
    
    # Registrar comandos
    bot_app.add_handler(CommandHandler("start", start_command))
    bot_app.add_handler(CommandHandler("estado", estado_command))
    bot_app.add_handler(CommandHandler("alertas", alertas_command))
    bot_app.add_handler(CommandHandler("historial", historial_command))
    bot_app.add_handler(CommandHandler("grafico", grafico_command))
    bot_app.add_handler(CommandHandler("silenciar", silenciar_command))
    bot_app.add_handler(CallbackQueryHandler(callback_query_handler))
    
    # Inicializar la app
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling()
    
    logger.info("✅ Bot de Telegram SIGEGEN-alert iniciado.")
    return bot_app

async def start_telegram_bot():
    """Función para arrancar en el evento startup de FastAPI"""
    asyncio.create_task(init_telegram_bot())

async def stop_telegram_bot():
    """Detiene el bot durante el shutdown de FastAPI"""
    global bot_app
    if bot_app:
        await bot_app.updater.stop()
        await bot_app.stop()
        await bot_app.shutdown()
        logger.info("🛑 Bot de Telegram detenido.")

async def send_telegram_alert(message: str, chat_id: str = None):
    """Envía una alerta proactiva desde el backend."""
    global bot_app
    if not bot_app:
        return
        
    settings = get_settings()
    target_chat_id = chat_id or settings.telegram_chat_id
    
    if not target_chat_id:
        return
        
    # Verificar si el chat está silenciado
    target_chat_id = int(target_chat_id)
    if target_chat_id in MUTED_UNTIL:
        if datetime.now() < MUTED_UNTIL[target_chat_id]:
            logger.info("Alerta silenciada por el usuario.")
            return
        else:
            del MUTED_UNTIL[target_chat_id]
            
    try:
        await bot_app.bot.send_message(chat_id=target_chat_id, text=message, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error enviando alerta a Telegram: {e}")
