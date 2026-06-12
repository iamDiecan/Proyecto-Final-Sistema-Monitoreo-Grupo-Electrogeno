# sigen/state/telegram_state.py
import reflex as rx

class TelegramState(rx.State):
    """Estado para la configuración de Telegram."""
    bot_token: str = ""
    chat_id: str = ""
    notifications_active: bool = False
    
    def set_bot_token(self, value: str):
        self.bot_token = value
        
    def set_chat_id(self, value: str):
        self.chat_id = value
        
    def set_notifications_active(self, value: bool):
        self.notifications_active = value
    
    def test_message(self):
        """Simula el envío de un mensaje de prueba."""
        if not self.bot_token or not self.chat_id:
            return rx.window_alert("Por favor, ingrese el Token y el Chat ID primero.")
        return rx.window_alert(f"Mensaje de prueba simulado enviado al Chat ID {self.chat_id}")
        
    def save_config(self):
        return rx.window_alert("Configuración guardada exitosamente en memoria.")
