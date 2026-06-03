# sigen/templates/template.py
import reflex as rx
from sigen.components.sidebar import sidebar
from sigen.styles import BG_COLOR, TEXT_COLOR, MUTED_TEXT, ACCENT_COLOR
from sigen.state.generador_state import GeneradorState

def top_header() -> rx.Component:
    """Barra superior con información en tiempo real y controles globales."""
    return rx.hstack(
        # Búsqueda o título de contexto
        rx.hstack(
            rx.icon(tag="database", size=18, color="#10B981"),
            rx.text("Base de Datos: Conectada", size="2", font_weight="500", color="#10B981"),
            spacing="2",
            align="center"
        ),
        
        rx.spacer(),
        
        # Estado de carga y Botón de actualización
        rx.hstack(
            rx.cond(
                GeneradorState.loading,
                rx.text("Actualizando...", size="2", color=MUTED_TEXT),
                rx.text("Datos al día", size="2", color=MUTED_TEXT)
            ),
            rx.icon_button(
                rx.icon(tag="refresh-cw", size=16),
                on_click=GeneradorState.periodic_refresh,
                variant="ghost",
                color_scheme="indigo",
                cursor="pointer",
            ),
            spacing="3",
            align="center"
        ),
        
        width="100%",
        padding="1rem 2rem",
        border_bottom="1px solid rgba(255, 255, 255, 0.05)",
        background="rgba(13, 17, 34, 0.5)",
        backdrop_filter="blur(8px)",
        position="sticky",
        top="0",
        z_index="99"
    )

def template(page_content: rx.Component) -> rx.Component:
    """Wrapper para todas las páginas que inyecta la barra lateral y cabecera."""
    return rx.hstack(
        sidebar(),
        
        # Contenedor del contenido principal
        rx.vstack(
            top_header(),
            
            # Contenido específico de la página
            rx.box(
                page_content,
                width="100%",
                padding="2rem",
                background=BG_COLOR,
                min_height="calc(100vh - 60px)"
            ),
            width="100%",
            margin_left="260px",  # Espacio para el sidebar fijo
            spacing="0",
        ),
        background=BG_COLOR,
        min_height="100vh",
        width="100%",
        spacing="0"
    )