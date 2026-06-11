# sigen-frontend/sigen/pages/alerts_center.py
import reflex as rx
from typing import List, Dict, Any
from sigen.templates.template import template
from sigen.styles import CARD_BG, CARD_BORDER, TEXT_COLOR, MUTED_TEXT
from sigen.state.alert_state import AlertState

def alert_row(alert: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(alert["node"].to(str), font_weight="bold"),
        rx.table.cell(rx.badge(alert["level"].to(str), color_scheme=alert["color"].to(str))),
        rx.table.cell(alert["title"].to(str)),
        rx.table.cell(alert["status"].to(str)),
        rx.table.cell(
            rx.button("Resolver", size="1", color_scheme="green", variant="soft")
        )
    )

def alerts_center() -> rx.Component:
    """Centro Integral de Alertas."""
    return template(
        rx.vstack(
            rx.heading("Centro de Alertas", size="8", margin_bottom="1rem", color=TEXT_COLOR),
            rx.text("Gestión y resolución de alertas de anomalías.", color=MUTED_TEXT, margin_bottom="2rem"),
            
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Nodo"),
                            rx.table.column_header_cell("Nivel"),
                            rx.table.column_header_cell("Título"),
                            rx.table.column_header_cell("Estado"),
                            rx.table.column_header_cell("Acciones"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(AlertState.alerts, alert_row)
                    ),
                    variant="surface",
                    size="2",
                    width="100%"
                ),
                background=CARD_BG,
                border=CARD_BORDER,
                padding="1rem",
                border_radius="16px",
                width="100%"
            )
        )
    )
