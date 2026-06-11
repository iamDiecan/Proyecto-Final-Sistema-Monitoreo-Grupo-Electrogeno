# sigen/pages/alertas.py
import reflex as rx
from sigen.templates.template import template
from sigen.components.alerts import alert_item
from sigen.state.generador_state import GeneradorState
from sigen.styles import MUTED_TEXT, TEXT_COLOR, CARD_BG, CARD_BORDER, glass_card_style

def alertas_content() -> rx.Component:
    """Contenido del panel de alertas."""
    return rx.vstack(
        # Título y Subtítulo
        rx.vstack(
            rx.heading("Historial de Alertas en Tiempo Real", size="8", font_weight="700"),
            rx.text("Gestión centralizada de eventos anómalos y diagnósticos difusos.", size="3", color=MUTED_TEXT),
            align_items="start",
            spacing="1"
        ),
        
        # Filtros
        rx.box(
            rx.grid(
                rx.input(
                    placeholder="Buscar por nodo o ubicación...",
                    value=GeneradorState.filtro_alerta_nodo,
                    on_change=GeneradorState.set_filtro_alerta_nodo,
                    width="100%",
                ),
                rx.select(
                    ["Todas", "Emergencia", "Crítico", "Alerta", "Precaución"],
                    value=GeneradorState.filtro_alerta_tipo,
                    on_change=GeneradorState.set_filtro_alerta_tipo,
                    width="100%"
                ),
                columns=rx.breakpoints(initial="1", md="2"),
                spacing="3",
                width="100%"
            ),
            background="rgba(255, 255, 255, 0.02)",
            padding="1rem",
            border_radius="12px",
            border="1px solid rgba(255, 255, 255, 0.05)",
            width="100%",
            margin_bottom="1rem"
        ),
        
        # Historial de alertas
        rx.box(
            rx.cond(
                GeneradorState.alertas_filtradas.length() > 0,
                rx.box(
                    rx.vstack(
                        rx.foreach(
                            GeneradorState.alertas_filtradas,
                            alert_item
                        ),
                        spacing="3",
                        width="100%"
                    ),
                    width="100%"
                ),
                rx.box(
                    rx.center(
                        rx.vstack(
                            rx.icon(tag="shield-check", size=48, color="#10B981"),
                            rx.text("No se encontraron alertas que coincidan con los filtros.", color=MUTED_TEXT, size="3"),
                            spacing="2",
                            align="center",
                        ),
                        style=glass_card_style,
                        width="100%",
                        padding="5rem 0"
                    ),
                    width="100%"
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
