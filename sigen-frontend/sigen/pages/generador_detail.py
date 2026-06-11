# sigen/pages/generador_detail.py
import reflex as rx
from sigen.templates.template import template
from sigen.components.cards import metric_card
from sigen.components.charts import telemetry_chart
from sigen.components.digital_twin import digital_twin
from sigen.components.health_gauge import health_gauge
from sigen.state.generador_state import GeneradorState
from sigen.styles import TEXT_COLOR, MUTED_TEXT, ACCENT_COLOR, CARD_BG, CARD_BORDER

def detail_stat(label: str, value: str, icon_tag: str, color: str = "#E2E8F0") -> rx.Component:
    """Muestra un valor individual con ícono y etiqueta en rejillas de datos."""
    return rx.hstack(
        rx.center(
            rx.icon(tag=icon_tag, size=16, color=color),
            background=f"{color}15",
            padding="8px",
            border_radius="8px"
        ),
        rx.vstack(
            rx.text(label, size="1", color=MUTED_TEXT, font_weight="500"),
            rx.text(value, size="3", font_weight="600", color=TEXT_COLOR),
            align_items="start",
            spacing="0"
        ),
        spacing="3",
        align="center",
        padding="0.5rem",
        border_radius="10px",
        background="rgba(255,255,255,0.01)",
        border="1px solid rgba(255,255,255,0.03)"
    )

def generador_detail_content() -> rx.Component:
    """Cuerpo de la página de detalle."""
    gen = GeneradorState.selected_generador
    
    return rx.vstack(
        # Cabecera de Navegación e Identificación
        rx.hstack(
            rx.button(
                rx.hstack(
                    rx.icon(tag="arrow-left", size=16),
                    rx.text("Volver al Dashboard"),
                    spacing="2",
                    align="center"
                ),
                on_click=lambda: rx.redirect("/dashboard"),
                variant="outline",
                color_scheme="gray",
                cursor="pointer",
            ),
            rx.spacer(),
            # status_badge(gen.get("estado", "desconocido")), # Se asume manejado por el nuevo layout o componentes
            align="center",
            width="100%"
        ),
        
        # Título del Generador
        rx.vstack(
            rx.heading(gen.get("nombre_completo", "Generador"), size="8", font_weight="700", margin_top="1rem"),
            align_items="start",
            spacing="1"
        ),

        # ── Primera Fila: Gemelo Digital y Salud ──────────────────────
        rx.grid(
            # Columna 1: Gemelo Digital (2/3 de ancho)
            rx.box(
                rx.vstack(
                    rx.heading("Visualización en Tiempo Real", size="4", color=TEXT_COLOR, margin_bottom="1rem"),
                    digital_twin(
                        estado=gen["estado"],
                        temp=gen["temp_motor_c"],
                        rpm=gen["rpm"],
                        voltaje=gen["voltaje_v"],
                        combustible=gen["combustible_pct"]
                    ),
                    align="start",
                    width="100%"
                ),
                background=CARD_BG,
                border=CARD_BORDER,
                padding="1.5rem",
                border_radius="16px",
            ),
            
            # Columna 2: Health Score y Alertas
            rx.box(
                rx.vstack(
                    rx.heading("Health Score", size="4", color=TEXT_COLOR, margin_bottom="1rem"),
                    rx.center(
                        health_gauge(
                            gen.get("health_score", 0.0).to(float), 
                            100
                        ),
                        width="100%",
                    ),
                    
                    rx.divider(margin_y="1rem"),
                    
                    rx.heading("Estado Difuso", size="3", color=TEXT_COLOR, margin_bottom="0.5rem"),
                    rx.text(
                        gen["alerta_nivel_str"], 
                        color=gen["alert_color"],
                        font_weight="bold",
                        size="5"
                    ),
                    
                    align="start",
                    width="100%"
                ),
                background=CARD_BG,
                border=CARD_BORDER,
                padding="1.5rem",
                border_radius="16px",
            ),
            columns=rx.breakpoints(initial="1", md="2"),
            spacing="4",
            width="100%",
            margin_bottom="2rem"
        ),
        
        # ── Segunda Fila: Métricas Numéricas ──────────────────────────
        rx.grid(
            metric_card("Voltaje", gen["voltaje_str"], "zap", "#F59E0B", "Frecuencia: " + gen["frecuencia_hz"].to_string() + " Hz"),
            metric_card("Temperatura", gen["temp_motor_str"], "thermometer", "#EF4444", "Ambiente: " + gen["temp_ambiente_c"].to_string() + " °C"),
            metric_card("Combustible", gen["combustible_str"], "droplet", "#3B82F6", "Consumo: " + gen["consumo_lh"].to_string() + " L/h"),
            metric_card("Conectividad", gen["rssi_str"], "wifi", "#10B981", "Batería: " + gen["bateria_v"].to_string() + " V"),
            columns=rx.breakpoints(initial="1", sm="2", md="2", lg="4"),
            spacing="5",
            width="100%",
            margin_bottom="2rem"
        ),
        
        # Gráficos Históricos y Filtros Temporales
        rx.vstack(
            rx.hstack(
                rx.heading("Historial de Telemetría", size="5", font_weight="600"),
                rx.spacer(),
                rx.select(
                    ["Última hora (Tiempo Real)", "Últimas 24 Horas", "Últimos 7 Días", "Últimos 30 Días"],
                    default_value="Última hora (Tiempo Real)",
                    width="200px"
                ),
                width="100%",
                align="center",
                margin_bottom="1rem"
            ),
            
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger("Voltaje", value="voltaje"),
                    rx.tabs.trigger("Corriente", value="corriente"),
                    rx.tabs.trigger("Potencia", value="potencia"),
                    rx.tabs.trigger("Frecuencia", value="frecuencia"),
                    rx.tabs.trigger("Temperatura", value="temperatura"),
                    rx.tabs.trigger("Combustible", value="combustible"),
                ),
                rx.tabs.content(
                    telemetry_chart(GeneradorState.historial_telemetria, "voltaje_v", "#4F46E5", "rgba(79,70,229,0.15)"),
                    value="voltaje"
                ),
                rx.tabs.content(
                    telemetry_chart(GeneradorState.historial_telemetria, "corriente_a", "#06B6D4", "rgba(6,182,212,0.15)"),
                    value="corriente"
                ),
                rx.tabs.content(
                    telemetry_chart(GeneradorState.historial_telemetria, "potencia_kw", "#10B981", "rgba(16,185,129,0.15)"),
                    value="potencia"
                ),
                rx.tabs.content(
                    telemetry_chart(GeneradorState.historial_telemetria, "frecuencia_hz", "#F59E0B", "rgba(245,158,11,0.15)"),
                    value="frecuencia"
                ),
                rx.tabs.content(
                    telemetry_chart(GeneradorState.historial_telemetria, "temp_motor_c", "#EF4444", "rgba(239,68,68,0.15)"),
                    value="temperatura"
                ),
                rx.tabs.content(
                    telemetry_chart(GeneradorState.historial_telemetria, "combustible_pct", "#B000FF", "rgba(176,0,255,0.15)"),
                    value="combustible"
                ),
                width="100%",
            ),
            background=CARD_BG,
            border=CARD_BORDER,
            padding="1.5rem",
            border_radius="16px",
            width="100%",
            align_items="start",
        ),
        
        # Historial de Alarmas y KPIs de Mantenimiento
        rx.grid(
            # Tabla de Alarmas
            rx.box(
                rx.vstack(
                    rx.heading("Historial de Alarmas", size="4", margin_bottom="1rem"),
                    rx.cond(
                        GeneradorState.historial_alertas_generador.length() > 0,
                        rx.vstack(
                            rx.foreach(
                                GeneradorState.historial_alertas_generador,
                                lambda a: rx.hstack(
                                    rx.text(a["timestamp_friendly"], size="1", color=MUTED_TEXT, width="120px"),
                                    rx.badge(a["alerta_difusa_categoria_friendly"].to(str), color_scheme=a["color_alerta"].to(str)),
                                    rx.text(a["estado_upper"].to(str), size="2", font_weight="bold"),
                                    width="100%",
                                    align="center",
                                    padding="0.5rem 0",
                                    border_bottom="1px solid rgba(255,255,255,0.05)"
                                )
                            ),
                            width="100%",
                            max_height="300px",
                            overflow_y="auto"
                        ),
                        rx.text("No se registraron alarmas recientes en este equipo.", color=MUTED_TEXT)
                    ),
                ),
                background=CARD_BG, border=CARD_BORDER, padding="1.5rem", border_radius="16px",
            ),
            # KPIs Mantenimiento
            rx.box(
                rx.vstack(
                    rx.heading("Indicadores de Salud (RAM)", size="4", margin_bottom="1rem"),
                    rx.vstack(
                        detail_stat("Disponibilidad Mensual", "99.8%", "activity", "#10B981"),
                        detail_stat("MTBF (Tiempo medio entre fallas)", "740 horas", "clock", "#3B82F6"),
                        detail_stat("MTTR (Tiempo medio de reparación)", "2.5 horas", "wrench", "#F59E0B"),
                        detail_stat("Horas de Operación Totales", gen.get("horas_motor_friendly", "0 hs"), "power", "#8B5CF6"),
                        width="100%",
                        spacing="3"
                    )
                ),
                background=CARD_BG, border=CARD_BORDER, padding="1.5rem", border_radius="16px",
            ),
            columns=rx.breakpoints(initial="1", lg="2"),
            spacing="4",
            width="100%",
        ),
        
        width="100%",
        spacing="4",
        align_items="stretch"
    )

def generador_detail() -> rx.Component:
    """Página del detalle de generador."""
    return template(generador_detail_content())