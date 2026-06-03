# sigen/components/cards.py
"""
Componentes de tarjetas reutilizables para SIGEGEN.
Usa colores y estilos desde styles.py.
"""
import reflex as rx
from sigen.state.generador_state import GeneradorState
from sigen.styles import (
    CARD_BG, CARD_BORDER, MUTED_TEXT, TEXT_COLOR,
    ACCENT_COLOR, ACCENT_CYAN, glass_card_style,
)


def status_badge(estado: rx.Var) -> rx.Component:
    """Badge de estado con color dinámico."""
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
        background=CARD_BG,
        border=CARD_BORDER,
        backdrop_filter="blur(12px)",
        border_radius="16px",
        padding="1.5rem",
        box_shadow="0 8px 32px 0 rgba(0, 0, 0, 0.3)",
        transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        _hover={
            "transform": "translateY(-4px)",
            "box_shadow": "0 12px 40px 0 rgba(0, 0, 0, 0.4)",
            "border": f"1px solid {icon_color}40",
        },
        width="100%",
    )


def generator_card(gen: rx.Var) -> rx.Component:
    """Tarjeta de generador con glassmorphism y hover effects."""
    return rx.box(
        rx.vstack(
            # ── Cabecera ──────────────────────────────────
            rx.hstack(
                rx.vstack(
                    rx.heading(gen["nombre_completo"], size="3", color=TEXT_COLOR),
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
                    size="2",
                    variant="soft",
                ),
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
                        rx.icon(tag="droplet", size=14, color=ACCENT_CYAN),
                        rx.text("Combustible", size="1", color=MUTED_TEXT),
                        spacing="1",
                        align="center",
                    ),
                    rx.text(gen["combustible_str"], size="1", font_weight="600", color=TEXT_COLOR),
                    justify="between",
                    width="100%",
                ),
                rx.progress(
                    value=gen["combustible_pct"],
                    width="100%",
                    height="6px",
                    # Color fijo - sin comparaciones
                    color_scheme="green",
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
        # ── Estilos glassmorphism ─────────────────────────
        background=CARD_BG,
        border=CARD_BORDER,
        backdrop_filter="blur(12px)",
        border_radius="16px",
        padding="1.5rem",
        box_shadow="0 8px 32px 0 rgba(0, 0, 0, 0.3)",
        width="100%",
        transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        _hover={
            "transform": "translateY(-4px)",
            "box_shadow": "0 16px 48px 0 rgba(0, 0, 0, 0.45)",
            "border": "1px solid rgba(255, 255, 255, 0.15)",
        },
    )