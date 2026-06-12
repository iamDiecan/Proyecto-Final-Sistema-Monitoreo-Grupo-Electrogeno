# sigen-frontend/sigen/components/kpi_cards.py
import reflex as rx
from sigen.styles import CARD_BG, CARD_BORDER, MUTED_TEXT, TEXT_COLOR

def kpi_card_mini(title: str, value: str, icon_tag: str, color: str = "#4F46E5") -> rx.Component:
    """Tarjeta KPI pequeña para dashboards densos."""
    return rx.box(
        rx.hstack(
            rx.center(
                rx.icon(tag=icon_tag, size=18, color=color),
                background=f"{color}15",
                padding="8px",
                border_radius="10px",
            ),
            rx.vstack(
                rx.text(title, size="1", color=MUTED_TEXT, font_weight="500"),
                rx.text(value, size="4", font_weight="bold", color=TEXT_COLOR),
                spacing="0",
                align="start"
            ),
            spacing="3",
            align="center",
        ),
        background=CARD_BG,
        border=CARD_BORDER,
        border_radius="12px",
        padding="1rem",
        width="100%",
        transition="transform 0.2s ease",
        _hover={
            "transform": "translateY(-2px)"
        }
    )
