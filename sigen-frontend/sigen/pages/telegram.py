# sigen-frontend/sigen/pages/telegram.py
import reflex as rx
from sigen.templates.template import template
from sigen.styles import CARD_BG, CARD_BORDER, TEXT_COLOR, MUTED_TEXT
from sigen.state.telegram_state import TelegramState

def telegram() -> rx.Component:
    """Página de configuración del bot de Telegram."""
    return template(
        rx.vstack(
            rx.heading("Integración con Telegram", size="8", margin_bottom="1rem", color=TEXT_COLOR),
            rx.text("Configura el bot para recibir alertas críticas en tiempo real.", color=MUTED_TEXT, margin_bottom="2rem"),
            
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.icon(tag="bot", size=24, color="#0088CC"),
                        rx.heading("Ajustes del Bot", size="5", color=TEXT_COLOR),
                        spacing="2",
                        align="center"
                    ),
                    rx.divider(margin_y="1rem"),
                    
                    rx.vstack(
                        rx.text("Bot Token", size="2", font_weight="bold", color=MUTED_TEXT),
                        rx.input(
                            placeholder="Ej: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
                            value=TelegramState.bot_token,
                            on_change=TelegramState.set_bot_token,
                            type="password",
                            width="100%"
                        ),
                        
                        rx.text("Chat ID del Grupo o Administrador", size="2", font_weight="bold", color=MUTED_TEXT, margin_top="1rem"),
                        rx.input(
                            placeholder="Ej: -100123456789",
                            value=TelegramState.chat_id,
                            on_change=TelegramState.set_chat_id,
                            width="100%"
                        ),
                        
                        rx.hstack(
                            rx.text("Activar notificaciones de alertas", size="2", font_weight="bold", color=MUTED_TEXT),
                            rx.spacer(),
                            rx.switch(
                                checked=TelegramState.notifications_active,
                                on_change=TelegramState.set_notifications_active,
                                color_scheme="green"
                            ),
                            width="100%",
                            align="center",
                            margin_top="1.5rem",
                            padding="1rem",
                            background="rgba(255, 255, 255, 0.02)",
                            border_radius="8px"
                        ),
                        width="100%",
                        align="start"
                    ),
                    
                    rx.hstack(
                        rx.button("Guardar Configuración", icon="save", color_scheme="blue", variant="solid", on_click=TelegramState.save_config),
                        rx.button("Enviar Prueba", icon="send", color_scheme="green", variant="soft", on_click=TelegramState.test_message),
                        spacing="3",
                        margin_top="2rem"
                    ),
                    
                    align="start",
                    width="100%"
                ),
                background=CARD_BG,
                border=CARD_BORDER,
                padding="2rem",
                border_radius="16px",
                width="100%",
                max_width="600px"
            )
        )
    )
