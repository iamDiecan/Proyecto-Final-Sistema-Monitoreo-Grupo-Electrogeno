# sigen/pages/dashboard.py
import reflex as rx
from sigen.templates.template import template
from sigen.components.cards import metric_card, generator_card
from sigen.state.generador_state import GeneradorState
from sigen.styles import MUTED_TEXT, TEXT_COLOR

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

def dashboard_content() -> rx.Component:
    """Contenido principal del dashboard."""
    return rx.vstack(
        # Título y Subtítulo
        rx.vstack(
            rx.heading("Panel de Control SIGEGEN", size="8", font_weight="700"),
            rx.text("Monitoreo inteligente de grupos electrógenos en tiempo real - Formosa", size="3", color=MUTED_TEXT),
            align_items="start",
            spacing="1"
        ),
        
        # Tarjetas de Resumen
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
        
        # Barra de Filtros
        filter_bar(),
        
        # Grid de Generadores
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
                    rx.text("No se encontraron generadores con los filtros seleccionados.", color=MUTED_TEXT, size="3"),
                    spacing="2",
                    align="center",
                ),
                width="100%",
                padding="4rem 0"
            )
        ),
        
        width="100%",
        spacing="4",
        align_items="stretch"
    )

def dashboard() -> rx.Component:
    """Página del Dashboard principal."""
    return template(dashboard_content())
