# sigen/components/cards.py
import reflex as rx
from sigen.state.generador_state import GeneradorState

# Estilos simplificados (usa valores por defecto si no existen)
TEXT_COLOR = "#1f2937"
MUTED_TEXT = "#6b7280"
ACCENT_COLOR = "#4f46e5"

def status_badge(estado: rx.Var) -> rx.Component:
    return rx.badge(
        estado,
        color_scheme=rx.cond(
            estado == "normal",
            "green",
            rx.cond(
                estado == "precaucion",
                "yellow",
                rx.cond(
                    estado == "alerta",
                    "orange",
                    "red"
                )
            )
        )
    )

def metric_card(title: str, value: str, icon_tag: str = None, icon_color: str = None, subtitle: str = "") -> rx.Component:
    """Tarjeta de métrica simplificada."""
    return rx.card(
        rx.vstack(
            rx.text(title, font_weight="500", color=MUTED_TEXT),
            rx.heading(value, size="2", font_weight="700"),
            rx.cond(
                subtitle,
                rx.text(subtitle, size="1", color=MUTED_TEXT),
            ),
            spacing="1",
            align="start",
        ),
        padding="1rem",
        width="100%",
    )

def generator_card(gen: rx.Var) -> rx.Component:
    """Tarjeta de generador simplificada using pre-formatted fields."""
    return rx.card(
        rx.vstack(
            # Cabecera
            rx.hstack(
                rx.vstack(
                    rx.heading(gen["nombre_completo"], size="3"),
                    rx.text(gen["zona_friendly"], size="1", color=MUTED_TEXT),
                    align_items="start",
                ),
                rx.badge(
                    gen["estado_upper"],
                    color_scheme=rx.cond(
                        gen["estado"] == "normal",
                        "green",
                        rx.cond(
                            gen["estado"] == "precaucion",
                            "yellow",
                            rx.cond(
                                gen["estado"] == "alerta",
                                "orange",
                                "red"
                            )
                        )
                    ),
                ),
                justify="between",
                width="100%",
            ),
            
            rx.divider(),
            
            # Métricas principales
            rx.grid(
                rx.vstack(
                    rx.text("Voltaje", size="1", color=MUTED_TEXT),
                    rx.text(gen["voltaje_str"], size="3", font_weight="600"),
                    align_items="start",
                ),
                rx.vstack(
                    rx.text("Temp. Motor", size="1", color=MUTED_TEXT),
                    rx.text(gen["temp_motor_str"], size="3", font_weight="600"),
                    align_items="start",
                ),
                rx.vstack(
                    rx.text("Señal RSSI", size="1", color=MUTED_TEXT),
                    rx.text(gen["rssi_str"], size="3", font_weight="600"),
                    align_items="start",
                ),
                columns="3",
                width="100%",
                spacing="2",
            ),
            
            rx.divider(),
            
            # Combustible con barra de progreso
            rx.vstack(
                rx.hstack(
                    rx.text("Combustible", size="1", color=MUTED_TEXT),
                    rx.text(gen["combustible_str"], size="1", font_weight="600"),
                    justify="between",
                    width="100%",
                ),
                rx.progress(value=gen["combustible_pct"], width="100%", height="8px"),
                width="100%",
                spacing="1",
            ),
            
            # Alerta difusa y botón
            rx.hstack(
                rx.vstack(
                    rx.text("Alerta Difusa", size="1", color=MUTED_TEXT),
                    rx.text(gen["alerta_nivel_str"], size="2", font_weight="600"),
                    align_items="start",
                ),
                rx.button(
                    "Detalles",
                    on_click=lambda: GeneradorState.ir_a_detalle(gen["nodo_id"]),
                    size="2",
                    variant="soft",
                    color_scheme="indigo",
                ),
                justify="between",
                width="100%",
                margin_top="8px",
            ),
            
            spacing="3",
            align="start",
        ),
        width="100%",
        _hover={"shadow": "lg"},
    )