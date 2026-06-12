# sigen/components/cards.py
"""
Componentes de tarjetas reutilizables para SIGEGEN.
Usa colores y estilos desde styles.py.
"""
import reflex as rx
from sigen.state.generador_state import GeneradorState
from sigen.styles import (
    CARD_BG, CARD_BORDER, MUTED_TEXT, TEXT_COLOR,
    ACCENT_CYAN, glass_card_style, PARAM_FUEL, GLOW_FUEL, GLOW_CYAN
)


def status_badge(estado_str: rx.Var, color_str: rx.Var = None) -> rx.Component:
    """Badge de estado con color estático e ícono dinámico."""
    return rx.badge(
        rx.match(
            estado_str,
            ("NORMAL", rx.icon(tag="check", size=14)),
            ("FALLA", rx.icon(tag="x", size=14)),
            ("EMERGENCIA", rx.icon(tag="octagon-alert", size=14)),
            ("PRECAUCION", rx.icon(tag="triangle-alert", size=14)),
            ("ALERTA", rx.icon(tag="triangle-alert", size=14)),
            rx.icon(tag="info", size=14)
        ),
        estado_str,
        color_scheme=color_str,
        variant="soft",
        display="flex",
        align_items="center",
        gap="1"
    )

def led_indicator(background_color: rx.Var, box_shadow: rx.Var) -> rx.Component:
    return rx.box(
        width="10px",
        height="10px",
        border_radius="50%",
        background_color=background_color,
        box_shadow=box_shadow
    )


def metric_card(
    title: str,
    value: str,
    icon_tag: str = "activity",
    icon_color: str = "#4F46E5",
    subtitle: str = "",
) -> rx.Component:
    """Tarjeta de métrica con glassmorphism, ícono y micro-animaciones."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.center(
                    rx.icon(tag=icon_tag, size=22, color=icon_color),
                    background=f"{icon_color}15",
                    padding="10px",
                    border_radius="12px",
                ),
                rx.spacer(),
                width="100%",
            ),
            rx.heading(value, size="7", font_weight="700", color=TEXT_COLOR),
            rx.text(title, font_weight="500", color=MUTED_TEXT, size="2"),
            rx.cond(
                subtitle,
                rx.text(subtitle, size="1", color=MUTED_TEXT),
            ),
            spacing="2",
            align="start",
        ),
        **glass_card_style,
        width="100%",
    )


def generator_card(gen: rx.Var) -> rx.Component:
    """Tarjeta de generador con glassmorphism y hover effects."""
    return rx.box(
        rx.vstack(
            # ── Cabecera ──────────────────────────────────
            rx.hstack(
                rx.hstack(
                    led_indicator(gen["led_color"].to(str), gen["led_shadow"].to(str)),
                    rx.vstack(
                        rx.heading(gen["nombre_completo"], size="3", color=TEXT_COLOR),
                        rx.text(gen["zona_friendly"], size="1", color=MUTED_TEXT),
                        align_items="start",
                    ),
                    align="center",
                    spacing="2"
                ),
                status_badge(gen["estado_upper"].to(str), gen["estado_color"].to(str)),
                justify="between",
                width="100%",
            ),
            
            rx.divider(color="rgba(255, 255, 255, 0.06)"),
            
            # ── Métricas principales ──────────────────────
            rx.grid(
                rx.vstack(
                    rx.text("Voltaje", size="1", color=MUTED_TEXT),
                    rx.text(gen["voltaje_str"], size="3", font_weight="600", color=TEXT_COLOR),
                    align_items="start",
                ),
                rx.vstack(
                    rx.text("Temp. Motor", size="1", color=MUTED_TEXT),
                    rx.text(gen["temp_motor_str"], size="3", font_weight="600", color=TEXT_COLOR),
                    align_items="start",
                ),
                rx.vstack(
                    rx.text("Señal RSSI", size="1", color=MUTED_TEXT),
                    rx.text(gen["rssi_str"], size="3", font_weight="600", color=TEXT_COLOR),
                    align_items="start",
                ),
                columns="3",
                width="100%",
                spacing="2",
            ),
            
            rx.divider(color="rgba(255, 255, 255, 0.06)"),
            
            # ── Combustible con barra de progreso (CORREGIDO) ─────────
            rx.vstack(
                rx.hstack(
                    rx.hstack(
                        rx.icon(tag="droplet", size=14, color=PARAM_FUEL),
                        rx.text("Combustible", size="1", color=MUTED_TEXT),
                        spacing="1",
                        align="center",
                    ),
                    rx.text(gen["combustible_str"], size="1", font_weight="600", color=TEXT_COLOR),
                    justify="between",
                    width="100%",
                ),
                rx.progress(
                    value=gen["combustible_pct"].to(int),
                    width="100%",
                    height="6px",
                    # Color fijo - neutralizado para SCADA HMI
                    color_scheme="gray",
                    box_shadow=GLOW_FUEL
                ),
                width="100%",
                spacing="1",
            ),
            
            # ── Alerta difusa y botón ─────────────────────
            rx.hstack(
                rx.vstack(
                    rx.text("Alerta Difusa", size="1", color=MUTED_TEXT),
                    rx.hstack(
                        rx.text(gen["alerta_nivel_str"], size="2", font_weight="600", color=TEXT_COLOR),
                        spacing="1",
                        align="center",
                    ),
                    align_items="start",
                ),
                rx.button(
                    rx.hstack(
                        rx.text("Detalles"),
                        rx.icon(tag="arrow-right", size=14),
                        spacing="1",
                        align="center",
                    ),
                    on_click=lambda: GeneradorState.ir_a_detalle(gen["nodo_id"]),
                    size="2",
                    variant="soft",
                    color_scheme="indigo",
                    cursor="pointer",
                    border_radius="10px",
                ),
                justify="between",
                width="100%",
                margin_top="4px",
            ),
            
            spacing="3",
            align="start",
        ),
        **glass_card_style,
        width="100%",
    )