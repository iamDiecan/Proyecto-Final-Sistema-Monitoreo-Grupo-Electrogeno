# sigen-frontend/sigen/pages/login.py
import reflex as rx
from sigen.styles import BG_COLOR, CARD_BG, CARD_BORDER, TEXT_COLOR, MUTED_TEXT, ACCENT_COLOR
from sigen.state.auth_state import AuthState

def login() -> rx.Component:
    """Página de Login de SIGEGEN."""
    return rx.center(
        rx.vstack(
            # Logo/Header
            rx.vstack(
                rx.icon(tag="activity", size=48, color="#06B6D4"),
                rx.heading("SIGEGEN", size="8", font_weight="800", letter_spacing="0.05em", color=TEXT_COLOR),
                rx.text("Sistema Inteligente de Gestión de Grupos Electrógenos", size="2", color=MUTED_TEXT, text_align="center"),
                spacing="2",
                align="center",
                margin_bottom="2rem"
            ),
            
            # Login Card
            rx.box(
                rx.vstack(
                    rx.heading("Iniciar Sesión", size="5", margin_bottom="1rem", color=TEXT_COLOR),
                    
                    rx.cond(
                        AuthState.error_message != "",
                        rx.callout(
                            AuthState.error_message,
                            icon="triangle-alert",
                            color_scheme="red",
                            width="100%",
                            margin_bottom="1rem"
                        ),
                    ),
                    
                    rx.text("Usuario", size="2", color=MUTED_TEXT, margin_bottom="0.25rem"),
                    rx.input(
                        placeholder="Ingresar usuario...",
                        on_change=AuthState.set_username,
                        value=AuthState.username,
                        width="100%",
                        size="3",
                        margin_bottom="1rem"
                    ),
                    
                    rx.text("Contraseña", size="2", color=MUTED_TEXT, margin_bottom="0.25rem"),
                    rx.input(
                        placeholder="Ingresar contraseña...",
                        type="password",
                        on_change=AuthState.set_password,
                        value=AuthState.password,
                        width="100%",
                        size="3",
                        margin_bottom="1.5rem"
                    ),
                    
                    rx.button(
                        "Ingresar",
                        on_click=AuthState.login,
                        width="100%",
                        size="3",
                        color_scheme="indigo",
                        cursor="pointer"
                    ),
                    align="start",
                    width="100%"
                ),
                background=CARD_BG,
                border=CARD_BORDER,
                backdrop_filter="blur(12px)",
                border_radius="16px",
                padding="2.5rem",
                box_shadow="0 8px 32px 0 rgba(0, 0, 0, 0.3)",
                width="400px",
            ),
            
            # Footer
            rx.text("Provincia de Formosa © 2026", size="1", color=MUTED_TEXT, margin_top="2rem"),
            
            align="center",
        ),
        background=BG_COLOR,
        width="100vw",
        height="100vh",
        # Imagen de fondo decorativa
        background_image="radial-gradient(circle at 50% -20%, rgba(79, 70, 229, 0.15), transparent 50%)",
    )
