# sigen/pages/alertas.py
import reflex as rx
from sigen.templates.template import template
from sigen.components.alerts import alert_item
from sigen.state.generador_state import GeneradorState
from sigen.styles import MUTED_TEXT, glass_card_style

def alertas_content() -> rx.Component:
    """Contenido del panel de alertas."""
    return rx.vstack(
        # Título y Subtítulo
        rx.vstack(
            rx.heading("Historial de Alertas en Tiempo Real", size="8", font_weight="700"),
            rx.text("Eventos anómalos y diagnósticos difusos de los 30 generadores", size="3", color=MUTED_TEXT),
            align_items="start",
            spacing="1"
        ),
        
        # Historial de alertas
        rx.vstack(
            rx.cond(
                GeneradorState.alertas.length() > 0,
                rx.vstack(
                    rx.foreach(
                        GeneradorState.alertas,
                        alert_item
                    ),
                    spacing="3",
                    width="100%"
                ),
                rx.center(
                    rx.vstack(
                        rx.icon(tag="shield-check", size=48, color="#10B981"),
                        rx.text("Todos los nodos operan en condiciones óptimas. No hay alertas.", color=MUTED_TEXT, size="3"),
                        spacing="2",
                        align="center",
                    ),
                    style=glass_card_style,
                    width="100%",
                    padding="5rem 0"
                )
            ),
            width="100%",
            margin_top="1.5rem"
        ),
        width="100%",
        spacing="4",
        align_items="stretch"
    )

def alertas() -> rx.Component:
    """Página de alertas."""
    return template(alertas_content())
