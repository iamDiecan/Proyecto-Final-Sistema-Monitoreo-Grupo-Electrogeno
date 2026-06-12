# sigen/pages/inicio.py
"""
Página de Inicio Ejecutiva (Vista de alto nivel).
Diferenciada del Dashboard operativo.
"""
import reflex as rx
from sigen.templates.template import template
from sigen.components.kpi_cards import kpi_card_mini
from sigen.components.cards import status_badge
from sigen.styles import TEXT_COLOR, MUTED_TEXT, CARD_BG, CARD_BORDER, ACCENT_CYAN
from sigen.state.generador_state import GeneradorState

def inicio_content() -> rx.Component:
    """Contenido ejecutivo principal para la página de Inicio."""
    return rx.vstack(
        # ── Título Ejecutivo ────────────────────
        rx.hstack(
            rx.vstack(
                rx.heading("Resumen Ejecutivo de Red", size="8", font_weight="700"),
                rx.text(
                    "Panorama general del sistema de generación eléctrica provincial",
                    size="3",
                    color=MUTED_TEXT,
                ),
                align_items="start",
                spacing="1",
            ),
            rx.spacer(),
            width="100%",
            align="start",
        ),

        # ── KPIs Generales (Estado Provincial) ───────────────────────────────────────
        rx.grid(
            kpi_card_mini("Generadores Totales", f"{GeneradorState.resumen_global['total']}", "server", ACCENT_CYAN),
            kpi_card_mini("Activos / En Servicio", f"{GeneradorState.resumen_global['encendidos']}", "activity", "#10B981"),
            kpi_card_mini("Fuera de Servicio", f"{GeneradorState.resumen_global['apagados']}", "power-off", "#64748B"),
            kpi_card_mini("Alarmas Críticas", f"{GeneradorState.resumen_global['falla']}", "triangle-alert", "#EF4444"),
            columns=rx.breakpoints(initial="1", sm="2", md="4"),
            spacing="4",
            width="100%",
            margin_bottom="1rem"
        ),
        
        # ── Paneles Centrales ───────────────────────
        rx.grid(
            # Panel Izquierdo: Cobertura y Tendencias
            rx.vstack(
                rx.box(
                    rx.vstack(
                        rx.heading("Disponibilidad General", size="4", color=TEXT_COLOR),
                        rx.text("Proporción de nodos en línea y reportando.", size="1", color=MUTED_TEXT, margin_bottom="1rem"),
                        # Simulación de un gauge / progress bar
                        rx.progress(
                            value=GeneradorState.disponibilidad_pct, 
                            color_scheme="green",
                            height="20px",
                            border_radius="10px"
                        ),
                        rx.hstack(
                            rx.text("0%", size="1", color=MUTED_TEXT),
                            rx.spacer(),
                            rx.text("100%", size="1", color=MUTED_TEXT),
                            width="100%",
                            padding_top="4px"
                        ),
                        align="start",
                        width="100%"
                    ),
                    background=CARD_BG,
                    border=CARD_BORDER,
                    padding="1.5rem",
                    border_radius="16px",
                    width="100%",
                ),
                
                # Indicadores Rápidos Adicionales
                rx.grid(
                    rx.box(
                        rx.vstack(
                            rx.icon(tag="thermometer", size=24, color="#F59E0B"),
                            rx.heading("Temp. Promedio", size="2", color=MUTED_TEXT),
                            rx.heading("78 °C", size="6", color=TEXT_COLOR), # Simulado
                            align="start"
                        ),
                        background=CARD_BG, border=CARD_BORDER, padding="1.5rem", border_radius="16px",
                    ),
                    rx.box(
                        rx.vstack(
                            rx.icon(tag="droplet", size=24, color="#3B82F6"),
                            rx.heading("Combustible Global", size="2", color=MUTED_TEXT),
                            rx.heading(GeneradorState.combustible_promedio_str, size="6", color=TEXT_COLOR),
                            align="start"
                        ),
                        background=CARD_BG, border=CARD_BORDER, padding="1.5rem", border_radius="16px",
                    ),
                    columns="2",
                    spacing="4",
                    width="100%"
                ),
                width="100%",
                spacing="4"
            ),
            
            # Panel Derecho: Últimas Alarmas (Resumen)
            rx.vstack(
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.icon(tag="bell", size=20, color=TEXT_COLOR),
                            rx.heading("Alarmas Recientes", size="4", color=TEXT_COLOR),
                            rx.spacer(),
                            rx.button("Ver Todas", on_click=lambda: rx.redirect("/alertas"), size="1", variant="soft", color_scheme="indigo"),
                            width="100%",
                            align="center"
                        ),
                        rx.divider(margin_y="0.5rem", color="rgba(255, 255, 255, 0.05)"),
                        
                        rx.cond(
                            GeneradorState.alertas_inicio.length() > 0,
                            rx.box(
                                rx.vstack(
                                    rx.foreach(
                                        GeneradorState.alertas_inicio,
                                        lambda a: rx.hstack(
                                            rx.icon(tag="triangle-alert", size=14, color=a["alert_color"].to(str)),
                                            rx.text(a["nombre_completo"].to(str), size="2", font_weight="500", color=TEXT_COLOR),
                                            rx.spacer(),
                                            status_badge(a["estado_upper"].to(str), a["estado_color"].to(str)),
                                            width="100%",
                                            align="center",
                                            padding="0.5rem 0",
                                            border_bottom="1px solid rgba(255, 255, 255, 0.05)"
                                        )
                                    ),
                                    spacing="0",
                                    width="100%"
                                ),
                                width="100%"
                            ),
                            rx.box(
                                rx.text("No hay alarmas activas", color=MUTED_TEXT),
                                width="100%"
                            )
                        ),
                        width="100%",
                        align="start"
                    ),
                    background=CARD_BG,
                    border=CARD_BORDER,
                    padding="1.5rem",
                    border_radius="16px",
                    width="100%",
                    height="100%",
                    min_height="300px"
                ),
                width="100%",
            ),
            columns=rx.breakpoints(initial="1", lg="2"),
            spacing="6",
            width="100%"
        ),
        
        width="100%",
        spacing="6",
        align_items="stretch"
    )

def inicio() -> rx.Component:
    """Página Ejecutiva principal (Inicio)."""
    return template(inicio_content())
