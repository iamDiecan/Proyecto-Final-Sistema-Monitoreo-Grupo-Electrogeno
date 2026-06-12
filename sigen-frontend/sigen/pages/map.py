# sigen-frontend/sigen/pages/map.py
import reflex as rx
from sigen.templates.template import template
from sigen.styles import CARD_BG, CARD_BORDER, TEXT_COLOR, MUTED_TEXT

def map_page() -> rx.Component:
    """Mapa interactivo de nodos en Formosa."""
    
    return template(
        rx.vstack(
            rx.heading("Mapa Provincial de Nodos", size="8", margin_bottom="1rem", color=TEXT_COLOR),
            rx.text("Vista geográfica en tiempo real del estado de los grupos electrógenos.", color=MUTED_TEXT, margin_bottom="2rem"),
            
            rx.box(
                rx.center(
                    rx.vstack(
                        rx.icon(tag="map", size=64, color="#00E5FF", margin_bottom="1rem"),
                        rx.heading("Mapa Interactivo", size="6", color=TEXT_COLOR),
                        rx.badge("Próximamente", color_scheme="indigo", variant="solid", size="2"),
                        rx.text("La integración geográfica para la provincia de Formosa está en desarrollo.", color=MUTED_TEXT, text_align="center", max_width="400px"),
                        spacing="3",
                        align="center",
                        padding="4rem 2rem",
                    ),
                    width="100%",
                    height="500px",
                    background="rgba(17, 22, 44, 0.5)",
                    border_radius="12px",
                    border="1px dashed rgba(0, 229, 255, 0.3)",
                ),
                background=CARD_BG,
                border=CARD_BORDER,
                padding="1.5rem",
                border_radius="16px",
                width="100%",
                box_shadow="0 8px 32px 0 rgba(0, 0, 0, 0.3)"
            )
        ),
    )
