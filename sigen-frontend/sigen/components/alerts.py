# sigen/components/alerts.py
import reflex as rx
from typing import List
from sigen.styles import STATE_COLORS, MUTED_TEXT, TEXT_COLOR, glass_card_style
from sigen.components.cards import status_badge

def alert_item(alert: rx.Var) -> rx.Component:
    """Representa un ítem de alerta individual en el historial de eventos."""
    color = alert["alert_color"]
    
    return rx.hstack(
        # Indicador de color vertical a la izquierda
        rx.box(
            width="6px",
            height="100%",
            background=color.to(str),
            border_radius="4px 0 0 4px",
            position="absolute",
            left="0",
            top="0",
            animation=rx.cond(
                (alert["estado_upper"] == "FALLA") | (alert["estado_upper"] == "EMERGENCIA"),
                "scada-blink 1.5s infinite",
                "none"
            )
        ),
        
        # Contenido principal
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon(tag="bell-ring", size=18, color=color.to(str)),
                    rx.text(alert["nombre_completo"].to(str), size="3", font_weight="600"),
                    spacing="2",
                    align="center"
                ),
                rx.spacer(),
                status_badge(alert["estado_upper"].to(str), alert["estado_color"].to(str)),
                width="100%",
                align="center"
            ),
            
            rx.hstack(
                rx.text(alert["zona_friendly"].to(str), size="1", color=MUTED_TEXT, font_weight="500"),
                rx.text(" • ", size="1", color=MUTED_TEXT),
                rx.text(alert["alerta_difusa_nivel_friendly"].to(str), size="1", color=color.to(str), font_weight="600"),
                rx.text(" • ", size="1", color=MUTED_TEXT),
                rx.text(alert["timestamp_friendly"].to(str), size="1", color=MUTED_TEXT),
                align="center",
                spacing="2",
                margin_top="4px"
            ),
            
            rx.cond(
                alert["has_alarmas"].to(bool),
                rx.hstack(
                    rx.text("Alarmas detectadas:", size="1", color=MUTED_TEXT, font_weight="500"),
                    rx.hstack(
                        rx.foreach(
                            alert["alarmas"]._replace(_var_type=List[str]),
                            lambda alarm: rx.badge(alarm.to(str), color_scheme="red", variant="outline", font_size="0.65rem")
                        ),
                        spacing="1"
                    ),
                    spacing="2",
                    align="center",
                    margin_top="8px"
                ),
                rx.fragment()
            ),
            
            width="100%",
            align_items="start",
            spacing="1",
            padding_left="12px"
        ),
        
        background="rgba(255, 255, 255, 0.02)",
        border="1px solid rgba(255, 255, 255, 0.05)",
        border_radius="10px",
        padding="1rem",
        width="100%",
        position="relative",
        align="center",
        _hover={
            "background": "rgba(255, 255, 255, 0.04)",
            "border": alert["alert_border_hover"].to(str),
            "transition": "all 0.2s ease-in-out"
        }
    )