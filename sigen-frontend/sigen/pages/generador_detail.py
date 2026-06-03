# sigen/pages/generador_detail.py
import reflex as rx
from sigen.templates.template import template
from sigen.components.charts import telemetry_chart
from sigen.components.cards import status_badge
from sigen.state.generador_state import GeneradorState
from sigen.styles import glass_card_style, TEXT_COLOR, MUTED_TEXT, STATE_COLORS, ACCENT_COLOR

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

def fuzzy_bar(name: str, value: rx.Var, value_str: rx.Var) -> rx.Component:
    """Muestra la barra de contribución de una variable del motor de inferencia difuso."""
    # ✅ Calcular colores ANTES usando valores convertidos a float
    # Reflex pasa los valores como strings o números; convertimos a float para comparar
    try:
        valor_numerico = float(value) if value else 0
    except (ValueError, TypeError):
        valor_numerico = 0
    
    if valor_numerico > 75.0:
        color = "#EF4444"
    elif valor_numerico > 40.0:
        color = "#F97316"
    else:
        color = "#10B981"
    
    return rx.vstack(
        rx.hstack(
            rx.text(name, size="2", font_weight="500"),
            rx.spacer(),
            rx.text(value_str, size="2", font_weight="600", color=color),
            width="100%"
        ),
        rx.progress(
            value=value,
            width="100%",
            height="6px",
            border_radius="3px"
        ),
        width="100%",
        spacing="1"
    )

def generador_detail_content() -> rx.Component:
    """Cuerpo de la página de detalle."""
    gen = GeneradorState.selected_generador
    
    # ✅ Calcular valores y colores ANTES de usarlos en componentes
    try:
        alerta_nivel = float(gen.get("alerta_difusa_nivel", 0))
    except (ValueError, TypeError):
        alerta_nivel = 0
    
    if alerta_nivel > 75.0:
        alert_color = "#EF4444"
        alert_bg = "rgba(239, 68, 68, 0.15)"
    elif alerta_nivel > 35.0:
        alert_color = "#F97316"
        alert_bg = "rgba(249, 115, 22, 0.15)"
    else:
        alert_color = "#10B981"
        alert_bg = "rgba(16, 185, 129, 0.15)"
    
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
            status_badge(gen.get("estado", "desconocido")),
            align="center",
            width="100%"
        ),
        
        # Título del Generador
        rx.vstack(
            rx.heading(gen.get("nombre_completo", "Generador"), size="8", font_weight="700", margin_top="1rem"),
            rx.hstack(
                rx.text(gen.get("zona_friendly", ""), size="2", color=MUTED_TEXT, font_weight="600"),
                rx.cond(
                    gen.get("zona_friendly") & gen.get("coordenadas_friendly"),
                    rx.text(" • ", size="2", color=MUTED_TEXT),
                    rx.fragment()
                ),
                rx.text(gen.get("coordenadas_friendly", ""), size="2", color=MUTED_TEXT),
                rx.cond(gen.get("coordenadas_friendly") & gen.get("firmware_friendly"), rx.text(" • ", size="2", color=MUTED_TEXT), rx.fragment()),
                rx.text(gen.get("firmware_friendly", ""), size="2", color=MUTED_TEXT),
                align="center",
                spacing="2",
                wrap="wrap",
            ),
            align_items="start",
            spacing="1"
        ),
        
        # Grid Principal de Detalle
        rx.grid(
            # Columna Izquierda: Telemetría Técnica
            rx.vstack(
                rx.heading("Sensores y Telemetría Técnica", size="4", font_weight="600"),
                rx.grid(
                    detail_stat("Voltaje de Línea", gen.get("voltaje_friendly", "---"), "zap", "#06B6D4"),
                    detail_stat("Frecuencia", gen.get("frecuencia_friendly", "---"), "activity", "#10B981"),
                    detail_stat("Corriente Consumida", gen.get("corriente_friendly", "---"), "zap-off", "#8B5CF6"),
                    detail_stat("Potencia Activa", gen.get("potencia_friendly", "---"), "gauge", "#EC4899"),
                    detail_stat("Factor de Potencia", gen.get("factor_potencia_friendly", "---"), "sigma", "#64748B"),
                    detail_stat("Frecuencia Motor", gen.get("rpm_friendly", "---"), "workflow", "#F59E0B"),
                    detail_stat("Horas Acumuladas", gen.get("horas_motor_friendly", "---"), "clock", "#10B981"),
                    detail_stat("Voltaje Batería", gen.get("bateria_friendly", "---"), "battery", "#06B6D4"),
                    detail_stat("Uptime de Nodo", gen.get("uptime_friendly", "---"), "hourglass", "#64748B"),
                    detail_stat("Señal RSSI", gen.get("rssi_friendly", "---"), "wifi", "#64748B"),
                    columns="2",
                    spacing="3",
                    width="100%",
                    margin_top="1rem"
                ),
                
                # Nivel y consumo de combustible
                rx.vstack(
                    rx.heading("Gestión de Combustible", size="4", font_weight="600", margin_top="1.5rem"),
                    rx.vstack(
                        rx.hstack(
                            rx.text("Capacidad en Tanque", size="2", color=MUTED_TEXT),
                            rx.spacer(),
                            rx.text(gen.get("combustible_capacidad_friendly", "---"), size="2", font_weight="600"),
                            width="100%"
                        ),
                        rx.progress(
                            value=gen.get("combustible_pct", 0),
                            width="100%",
                            height="12px",
                            border_radius="6px"
                        ),
                        width="100%",
                        spacing="2"
                    ),
                    rx.grid(
                        detail_stat("Consumo Promedio", gen.get("consumo_friendly", "---"), "droplet", "#06B6D4"),
                        detail_stat("Autonomía Aprox.", gen.get("autonomia_friendly", "---"), "hourglass", "#10B981"),
                        columns="2",
                        spacing="3",
                        width="100%",
                        margin_top="0.5rem"
                    ),
                    style=glass_card_style,
                    width="100%",
                    align_items="start",
                    margin_top="1rem",
                    spacing="3"
                ),
                style=glass_card_style,
                width="100%",
                align_items="start",
                spacing="3"
            ),
            
            # Columna Derecha: Sistema Difuso e Historial
            rx.vstack(
                # Tarjeta de Inferencia Difusa
                rx.vstack(
                    rx.heading("Analizador de Alertas Difusas (Fuzzy Logic)", size="4", font_weight="600"),
                    rx.hstack(
                        rx.vstack(
                            rx.heading(gen.get("alerta_difusa_nivel_friendly", "0"), size="8", font_weight="700", color=alert_color),
                            rx.text(gen.get("alerta_difusa_categoria_friendly", "Normal"), size="2", color=alert_color, font_weight="600"),
                            align_items="start",
                            spacing="0"
                        ),
                        rx.spacer(),
                        rx.center(
                            rx.icon(tag="cpu", size=32, color=alert_color),
                            background=alert_bg,
                            padding="16px",
                            border_radius="16px"
                        ),
                        width="100%",
                        align="center"
                    ),
                    
                    rx.divider(color="rgba(255, 255, 255, 0.05)", margin_y="8px"),
                    
                    # Contribuciones de variables
                    rx.text("Desglose de Contribución de Sensores", size="2", color=MUTED_TEXT, font_weight="500"),
                    rx.vstack(
                        fuzzy_bar("Temperatura del Motor", gen.get("temp_contrib", 0), gen.get("temp_contrib_str", "0")),
                        fuzzy_bar("Estabilidad de Voltaje", gen.get("volt_contrib", 0), gen.get("volt_contrib_str", "0")),
                        fuzzy_bar("Reserva de Combustible", gen.get("comb_contrib", 0), gen.get("comb_contrib_str", "0")),
                        fuzzy_bar("Regulación de RPM", gen.get("rpm_contrib", 0), gen.get("rpm_contrib_str", "0")),
                        spacing="3",
                        width="100%",
                        margin_top="0.5rem"
                    ),
                    style=glass_card_style,
                    width="100%",
                    align_items="start",
                    spacing="3"
                ),
                
                # Gráficos Históricos
                rx.vstack(
                    rx.heading("Historial de Comportamiento (Últimas 20 mediciones)", size="4", font_weight="600"),
                    
                    rx.tabs.root(
                        rx.tabs.list(
                            rx.tabs.trigger("Temperatura", value="tab1"),
                            rx.tabs.trigger("Voltaje", value="tab2"),
                            rx.tabs.trigger("Combustible", value="tab3"),
                        ),
                        rx.tabs.content(
                            telemetry_chart(GeneradorState.historial_telemetria, "temp_motor_c", "#EF4444", "rgba(239,68,68,0.15)"),
                            value="tab1"
                        ),
                        rx.tabs.content(
                            telemetry_chart(GeneradorState.historial_telemetria, "voltaje_v", "#4F46E5", "rgba(79,70,229,0.15)"),
                            value="tab2"
                        ),
                        rx.tabs.content(
                            telemetry_chart(GeneradorState.historial_telemetria, "combustible_pct", "#06B6D4", "rgba(6,182,212,0.15)"),
                            value="tab3"
                        ),
                        width="100%",
                        margin_top="1rem"
                    ),
                    style=glass_card_style,
                    width="100%",
                    align_items="start",
                    margin_top="1.5rem"
                ),
                width="100%",
                spacing="4"
            ),
            columns="2",
            spacing="4",
            width="100%",
            margin_top="1.5rem"
        ),
        width="100%",
        spacing="4",
        align_items="stretch"
    )

def generador_detail() -> rx.Component:
    """Página del detalle de generador."""
    return template(generador_detail_content())