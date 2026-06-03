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
from sigen.templates.template import template
from sigen.components.cards import metric_card, generator_card
from sigen.state.generador_state import GeneradorState
from sigen.styles import MUTED_TEXT, TEXT_COLOR, CARD_BG, CARD_BORDER, ACCENT_CYAN


def error_banner() -> rx.Component:
    """Banner de error con ícono y botón de cerrar."""
    return rx.cond(
        GeneradorState.has_error,
        rx.box(
            rx.hstack(
                rx.icon(tag="alert-triangle", size=18, color="#FCD34D"),
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


def filter_bar() -> rx.Component:
    """Sección de filtros y buscador de generadores."""
    return rx.flex(
        # Buscador por texto
        rx.input(
            placeholder="Buscar por ID o Ciudad...",
            value=GeneradorState.filtro_busqueda,
            on_change=GeneradorState.set_filtro_busqueda,
            width="320px",
            size="3",
            radius="large",
        ),
        
        rx.spacer(),
        
        rx.hstack(
            # Selector de Zona
            rx.select(
                ["Todas", "Capital", "Norte", "Sur"],
                placeholder="Filtrar por Zona",
                value=GeneradorState.filtro_zona,
                on_change=GeneradorState.set_filtro_zona,
                size="3",
            ),
            
            # Selector de Estado
            rx.select(
                ["Todos", "Normal", "Alerta", "Falla"],
                placeholder="Filtrar por Estado",
                value=GeneradorState.filtro_estado,
                on_change=GeneradorState.set_filtro_estado,
                size="3",
            ),
            spacing="3",
            align="center"
        ),
        width="100%",
        padding="1rem",
        background="rgba(255, 255, 255, 0.02)",
        border="1px solid rgba(255, 255, 255, 0.05)",
        border_radius="12px",
        margin_y="1.5rem",
        align="center",
        direction="row",
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
        
        # ── Tarjetas de Resumen ───────────────────────────
        rx.grid(
            metric_card(
                title="Generadores Totales",
                value=GeneradorState.total_generadores,
                icon_tag="activity",
                icon_color="#4F46E5",
                subtitle=GeneradorState.resumen_subtitulo_totales
            ),
            metric_card(
                title="Alerta Promedio",
                value=GeneradorState.alerta_promedio_str,
                icon_tag="alert-triangle",
                icon_color="#F59E0B",
                subtitle="Nivel difuso global"
            ),
            metric_card(
                title="Sistemas en Falla",
                value=GeneradorState.falla_generadores,
                icon_tag="shield-alert",
                icon_color="#EF4444",
                subtitle="Requieren atención prioritaria"
            ),
            metric_card(
                title="Promedio Combustible",
                value=GeneradorState.combustible_promedio_str,
                icon_tag="droplet",
                icon_color="#06B6D4",
                subtitle="Nivel medio de tanques"
            ),
            columns="4",
            spacing="4",
            width="100%",
            margin_top="1.5rem"
        ),
        
        # ── Barra de Filtros ──────────────────────────────
        filter_bar(),
        
        # ── Grid de Generadores (con spinner y empty state) ──
        rx.cond(
            GeneradorState.loading,
            loading_overlay(),
            rx.cond(
                GeneradorState.generadores_filtrados.length() > 0,
                rx.grid(
                    rx.foreach(
                        GeneradorState.generadores_filtrados,
                        generator_card
                    ),
                    columns="3",
                    spacing="4",
                    width="100%"
                ),
                rx.center(
                    rx.vstack(
                        rx.icon(tag="search-code", size=48, color=MUTED_TEXT),
                        rx.text(
                            "No se encontraron generadores con los filtros seleccionados.",
                            color=MUTED_TEXT,
                            size="3",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    width="100%",
                    padding="4rem 0"
                )
            ),
        ),
        
        width="100%",
        spacing="4",
        align_items="stretch"
    )


def dashboard() -> rx.Component:
    """Página del Dashboard principal."""
    return template(dashboard_content())
