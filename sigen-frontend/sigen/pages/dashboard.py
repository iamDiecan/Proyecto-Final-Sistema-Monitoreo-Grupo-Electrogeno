# sigen/pages/dashboard.py
"""
Dashboard principal de SIGEGEN.
Incluye:
  - Banner de error con opción de dismiss
  - Badge de estado de conexión (InfluxDB / SQLite / Desconectado)
  - Spinner de carga durante la obtención de datos
  - Timestamp de última actualización
  - Filtros de zona, estado y búsqueda
"""
import reflex as rx
from sigen.components.cards import generator_card, metric_card
from sigen.components.charts import telemetry_chart
from sigen.components.alerts import alert_item
from sigen.components.kpi_cards import kpi_card_mini
from sigen.components.health_gauge import health_gauge
from sigen.templates.template import template
from sigen.styles import TEXT_COLOR, MUTED_TEXT, ACCENT_COLOR, CARD_BG, CARD_BORDER, CARD_BG, CARD_BORDER, ACCENT_CYAN
from sigen.state.generador_state import GeneradorState


def error_banner() -> rx.Component:
    """Banner de error con ícono y botón de cerrar."""
    return rx.cond(
        GeneradorState.has_error,
        rx.box(
            rx.hstack(
                rx.icon(tag="triangle-alert", size=18, color="#FCD34D"),
                rx.text(
                    GeneradorState.error,
                    size="2",
                    color="#FEF3C7",
                    flex="1",
                ),
                rx.icon_button(
                    rx.icon(tag="x", size=14),
                    on_click=GeneradorState.dismiss_error,
                    variant="ghost",
                    color_scheme="yellow",
                    size="1",
                    cursor="pointer",
                ),
                spacing="3",
                align="center",
                width="100%",
            ),
            background="rgba(180, 83, 9, 0.25)",
            border="1px solid rgba(251, 191, 36, 0.3)",
            border_radius="12px",
            padding="12px 16px",
            width="100%",
            backdrop_filter="blur(8px)",
        ),
    )


def connection_badge() -> rx.Component:
    """Badge que indica el estado de la fuente de datos."""
    return rx.hstack(
        rx.box(
            width="8px",
            height="8px",
            border_radius="50%",
            background=rx.cond(
                GeneradorState.is_influx_connected,
                "#10B981",
                rx.cond(
                    GeneradorState.datasource_mode == "sqlite_fallback",
                    "#F59E0B",
                    "#EF4444",
                ),
            ),
            box_shadow=rx.cond(
                GeneradorState.is_influx_connected,
                "0 0 8px rgba(16, 185, 129, 0.6)",
                "none",
            ),
        ),
        rx.text(
            GeneradorState.influx_status_text,
            size="1",
            color=MUTED_TEXT,
            font_weight="500",
        ),
        spacing="2",
        align="center",
        background="rgba(255, 255, 255, 0.03)",
        border="1px solid rgba(255, 255, 255, 0.06)",
        border_radius="20px",
        padding="4px 12px",
    )


def last_refresh_badge() -> rx.Component:
    """Badge que muestra la hora de la última actualización."""
    return rx.cond(
        GeneradorState.last_refresh,
        rx.hstack(
            rx.icon(tag="clock", size=12, color=MUTED_TEXT),
            rx.text(
                GeneradorState.last_refresh,
                size="1",
                color=MUTED_TEXT,
            ),
            spacing="1",
            align="center",
        ),
    )


def loading_overlay() -> rx.Component:
    """Spinner centrado de carga con mensaje."""
    return rx.center(
        rx.vstack(
            rx.spinner(size="3", color=ACCENT_CYAN),
            rx.text(
                "Cargando datos de generadores...",
                size="2",
                color=MUTED_TEXT,
            ),
            spacing="3",
            align="center",
        ),
        width="100%",
        padding="4rem 0",
    )


def dashboard_content() -> rx.Component:
    """Contenido principal del dashboard."""
    return rx.vstack(
        # ── Título, badges y subtítulo ────────────────────
        rx.hstack(
            rx.vstack(
                rx.heading("Panel de Control SIGEGEN", size="8", font_weight="700"),
                rx.text(
                    "Monitoreo inteligente de grupos electrógenos en tiempo real - Formosa",
                    size="3",
                    color=MUTED_TEXT,
                ),
                align_items="start",
                spacing="1",
            ),
            rx.spacer(),
            rx.vstack(
                connection_badge(),
                last_refresh_badge(),
                align="end",
                spacing="2",
            ),
            width="100%",
            align="start",
        ),

        # ── Banner de error (condicional) ─────────────────
        error_banner(),
        
        # ── KPIs Superiores ───────────────────────────────────────
        rx.grid(
            kpi_card_mini("Generadores Activos", f"{GeneradorState.resumen_global['encendidos']} / {GeneradorState.resumen_global['total']}", "zap", "#10B981"),
            kpi_card_mini("Alertas Críticas", f"{GeneradorState.resumen_global['falla']}", "triangle-alert", "#EF4444"),
            kpi_card_mini("Score Promedio", "85", "activity", "#3B82F6"),
            kpi_card_mini("Nodos Offline", "0", "wifi-off", "#64748B"),
            columns=rx.breakpoints(initial="1", sm="2", md="2", lg="4"),
            spacing="4",
            width="100%",
            margin_bottom="2rem"
        ),

        # ── Dashboard Principal: 2 Columnas ───────────────────────
        rx.grid(
            # Columna Izquierda: Nodos y Filtros (Jerárquico)
            rx.vstack(
                rx.hstack(
                    rx.heading("Red de Generadores", size="5", color=TEXT_COLOR),
                    rx.spacer(),
                    rx.badge(f"{GeneradorState.generadores_filtrados.length()} resultados", color_scheme="indigo"),
                    width="100%",
                    align="center",
                ),
                # Panel de Filtros
                rx.hstack(
                    rx.input(
                        placeholder="Buscar nodo, localidad...",
                        value=GeneradorState.filtro_busqueda,
                        on_change=GeneradorState.set_filtro_busqueda,
                        width="300px",
                    ),
                    rx.popover.root(
                        rx.popover.trigger(
                            rx.button(
                                rx.icon("filter", size=16),
                                "Filtros Avanzados",
                                variant="soft",
                                color_scheme="blue",
                            )
                        ),
                        rx.popover.content(
                            rx.vstack(
                                rx.text("Zona", size="2", font_weight="bold"),
                                rx.select(
                                    ["Toda la Provincia", "Capital", "Norte", "Sur"],
                                    value=GeneradorState.filtro_zona,
                                    on_change=GeneradorState.set_filtro_zona,
                                    width="100%"
                                ),
                                rx.text("Estado", size="2", font_weight="bold"),
                                rx.select(
                                    ["Todos", "Normal", "Precaucion", "Alerta", "Falla"],
                                    value=GeneradorState.filtro_estado,
                                    on_change=GeneradorState.set_filtro_estado,
                                    width="100%"
                                ),
                                rx.text("Combustible", size="2", font_weight="bold"),
                                rx.select(
                                    ["Todos", "Bajo (<20%)", "Crítico (<10%)"],
                                    value=GeneradorState.filtro_combustible,
                                    on_change=GeneradorState.set_filtro_combustible,
                                    width="100%"
                                ),
                                rx.text("Temperatura", size="2", font_weight="bold"),
                                rx.select(
                                    ["Todas", "Alta (>85°C)", "Crítica (>95°C)"],
                                    value=GeneradorState.filtro_temperatura,
                                    on_change=GeneradorState.set_filtro_temperatura,
                                    width="100%"
                                ),
                                spacing="3",
                                width="250px"
                            ),
                        )
                    ),
                    width="100%",
                    spacing="3",
                    margin_bottom="1rem"
                ),
                
                rx.cond(
                    GeneradorState.loading,
                    rx.box(loading_overlay(), width="100%"),
                    rx.box(
                        rx.cond(
                            GeneradorState.generadores_filtrados.length() > 0,
                            rx.box(
                                rx.grid(
                                    rx.foreach(
                                        GeneradorState.generadores_filtrados,
                                        generator_card
                                    ),
                                    columns=rx.breakpoints(initial="1", md="2"),
                                    spacing="4",
                                    width="100%",
                                    padding_top="1rem",
                                ),
                                width="100%"
                            ),
                            rx.box(
                                rx.center(
                                    rx.vstack(
                                        rx.icon(tag="circle-check", size=48, color="#10B981"),
                                        rx.heading("Todo en orden", size="4", color=TEXT_COLOR),
                                        rx.text("No hay generadores en alerta.", color=MUTED_TEXT),
                                        align="center"
                                    ),
                                    width="100%",
                                    height="300px",
                                    background=CARD_BG,
                                    border=CARD_BORDER,
                                    border_radius="16px",
                                ),
                                width="100%"
                            )
                        ),
                        width="100%"
                    )
                ),
                width="100%",
            ),
            
            # Columna Derecha: Resumen de Salud y Alertas
            rx.vstack(
                # Panel de Salud Global (Health Gauge)
                rx.box(
                    rx.vstack(
                        rx.heading("Salud Global de la Red", size="4", color=TEXT_COLOR),
                        rx.text("Índice ponderado basado en telemetría de todos los nodos", size="1", color=MUTED_TEXT, margin_bottom="1rem"),
                        rx.center(
                            health_gauge(85.0, 200),
                            width="100%",
                            padding="1rem"
                        ),
                        align="start",
                        width="100%"
                    ),
                    background=CARD_BG,
                    border=CARD_BORDER,
                    padding="1.5rem",
                    border_radius="16px",
                    width="100%",
                    box_shadow="0 8px 32px 0 rgba(0, 0, 0, 0.3)",
                ),
                
                # Panel de Alertas Recientes
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.heading("Alertas Recientes", size="4", color=TEXT_COLOR),
                            rx.spacer(),
                            rx.badge(
                                GeneradorState.alertas_recientes.length(),
                                color_scheme="red",
                                variant="solid"
                            ),
                            width="100%",
                        ),
                        rx.divider(margin_y="0.5rem", color="rgba(255, 255, 255, 0.06)"),
                        rx.cond(
                            GeneradorState.alertas_recientes.length() > 0,
                            rx.box(
                                rx.vstack(
                                    rx.foreach(
                                        GeneradorState.alertas_recientes,
                                        alert_item
                                    ),
                                    spacing="3",
                                    width="100%",
                                ),
                                width="100%"
                            ),
                            rx.box(
                                rx.text("No hay alertas recientes.", color=MUTED_TEXT, size="2"),
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
                    box_shadow="0 8px 32px 0 rgba(0, 0, 0, 0.3)",
                    margin_top="1.5rem"
                ),
                width="100%",
            ),
            columns=rx.breakpoints(initial="1", md="2"),
            spacing="6",
            width="100%"
        ),
        
        width="100%",
        spacing="4",
        align_items="stretch"
    )


def dashboard() -> rx.Component:
    """Página del Dashboard principal."""
    return template(dashboard_content())
