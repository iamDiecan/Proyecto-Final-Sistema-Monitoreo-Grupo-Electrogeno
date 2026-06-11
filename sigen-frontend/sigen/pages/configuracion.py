# sigen/pages/configuracion.py
import reflex as rx
from sigen.templates.template import template
from sigen.styles import MUTED_TEXT, glass_card_style, TEXT_COLOR

def rule_card(rule_num: int, condition: str, action: str, level: str) -> rx.Component:
    """Tarjeta compacta representando una regla difusa."""
    # Mapeo de colores SIGEGEN Ion
    color_map = {
        "normal": "#00FFAA",      # STATUS_SUCCESS
        "precaucion": "#FFB300",  # STATUS_WARNING
        "alerta": "#FFB300",      # STATUS_WARNING
        "critico": "#FF3366",     # STATUS_CRITICAL
        "emergencia": "#FF3366"   # STATUS_CRITICAL
    }
    color = color_map.get(level.lower(), "#00E5FF")
    bg_color = color.replace(")", ", 0.1)").replace("rgb", "rgba") if "rgb" in color else color + "15" # 15 is hex opacity ~8%
    
    return rx.box(
        rx.hstack(
            rx.badge(f"R{rule_num}", color_scheme="indigo", font_weight="700"),
            rx.text(condition, color=TEXT_COLOR, font_weight="500", size="2"),
            rx.spacer(),
            rx.icon(tag="arrow-right", size=16, color=MUTED_TEXT),
            rx.spacer(),
            rx.badge(action.upper(), style={"backgroundColor": bg_color, "color": color}, font_weight="700"),
            width="100%",
            align="center",
            spacing="3",
        ),
        background="rgba(255, 255, 255, 0.02)",
        border=f"1px solid rgba(255, 255, 255, 0.05)",
        border_radius="8px",
        padding="0.75rem 1rem",
        width="100%",
        _hover={"border": f"1px solid {color}50", "background": "rgba(255, 255, 255, 0.04)"},
        transition="all 0.2s ease"
    )

def variable_range(label: str, range_text: str, color: str) -> rx.Component:
    """Fila visual para rangos de variables."""
    return rx.hstack(
        rx.box(width="8px", height="8px", border_radius="50%", background=color),
        rx.text(label, font_weight="500", color=TEXT_COLOR, width="80px", size="2"),
        rx.badge(range_text, color_scheme="gray", variant="surface"),
        align="center",
        spacing="3",
        width="100%"
    )

def config_content() -> rx.Component:
    """Contenido del panel de configuración."""
    from sigen.state.config_state import ConfigState
    return rx.vstack(
        # Título y Subtítulo
        rx.vstack(
            rx.heading("Parámetros del Sistema y Lógica Difusa", size="8", font_weight="700"),
            rx.text("Configuración avanzada de las funciones de pertenencia y reglas de inferencia", size="3", color=MUTED_TEXT),
            align_items="start",
            spacing="1"
        ),
        
        # Tabs de Configuración
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("Simulación y Sistema", value="system"),
                rx.tabs.trigger("Reglas Difusas (Inferencia)", value="rules"),
                rx.tabs.trigger("Variables de Entrada", value="variables"),
            ),
            
            # Tab 0: Sistema
            rx.tabs.content(
                rx.vstack(
                    rx.heading("Simulación de Telemetría", size="4", font_weight="600"),
                    rx.text("Genera datos aleatorios simulando 30 nodos en Formosa para probar el comportamiento de alertas y reglas difusas.", color=MUTED_TEXT),
                    rx.hstack(
                        rx.button(
                            rx.cond(ConfigState.is_simulating, rx.spinner(size="2"), rx.icon(tag="play", size=16)),
                            rx.cond(ConfigState.is_simulating, "Simulando datos...", "Ejecutar Simulador (30 Nodos)"),
                            on_click=ConfigState.trigger_simulator,
                            disabled=ConfigState.is_simulating,
                            color_scheme="cyan",
                            variant="solid",
                            cursor="pointer"
                        ),
                        rx.cond(
                            ConfigState.status_message != "",
                            rx.text(ConfigState.status_message, color="#00E5FF", font_weight="500")
                        ),
                        align="center",
                        spacing="3",
                        margin_top="1rem"
                    ),
                    style=glass_card_style,
                    width="100%",
                    align_items="start",
                    margin_top="1rem"
                ),
                value="system"
            ),
            
            # Tab 1: Reglas de Inferencia
            rx.tabs.content(
                rx.vstack(
                    rx.hstack(
                        rx.icon(tag="cpu", color="#00E5FF", size=20),
                        rx.heading("Reglas de Control de Alertas", size="4", font_weight="600"),
                        align="center",
                        spacing="2",
                        margin_bottom="1rem"
                    ),
                    rx.grid(
                        rule_card(1, "Temperatura CRÍTICA", "Emergencia", "emergencia"),
                        rule_card(2, "Temp. ALTA y Voltaje BAJO", "Crítico", "critico"),
                        rule_card(3, "Temp. ALTA y Vibración ALTA", "Crítico", "critico"),
                        rule_card(4, "Combustible CRÍTICO", "Emergencia", "emergencia"),
                        rule_card(5, "Combustible BAJO y RPM ANORMAL", "Alerta", "alerta"),
                        rule_card(6, "Combustible BAJO y Temp. NORMAL", "Precaución", "precaucion"),
                        rule_card(7, "RPM BAJO o RPM ALTO", "Precaución", "precaucion"),
                        rule_card(8, "RPM ALTO y Vibración ALTA", "Crítico", "critico"),
                        rule_card(9, "Frecuencia FUERA DE RANGO", "Alerta", "alerta"),
                        rule_card(10, "Voltaje ALTO y Frecuencia ALTA", "Crítico", "critico"),
                        rule_card(11, "Todas las variables NORMALES", "Normal", "normal"),
                        rule_card(12, "Temp. ALTA y Combustible BAJO", "Crítico", "critico"),
                        columns=rx.breakpoints(initial="1", md="2"),
                        spacing="3",
                        width="100%"
                    ),
                    style=glass_card_style,
                    width="100%",
                    align_items="start",
                    margin_top="1rem"
                ),
                value="rules"
            ),
            
            # Tab 2: Funciones de Pertenencia
            rx.tabs.content(
                rx.grid(
                    # Temperatura
                    rx.vstack(
                        rx.hstack(rx.icon(tag="thermometer-sun", color="#FF007F", size=18), rx.heading("Temperatura", size="3", font_weight="600"), align="center"),
                        rx.divider(margin_y="0.5rem", color="rgba(255, 255, 255, 0.05)"),
                        variable_range("Baja", "0 - 50 °C", "#00E5FF"),
                        variable_range("Normal", "40 - 90 °C", "#00FFAA"),
                        variable_range("Alta", "80 - 120 °C", "#FFB300"),
                        variable_range("Crítica", "100 - 130 °C", "#FF3366"),
                        style=glass_card_style,
                        width="100%",
                        align_items="start",
                        spacing="2"
                    ),
                    # Voltaje
                    rx.vstack(
                        rx.hstack(rx.icon(tag="zap", color="#00E5FF", size=18), rx.heading("Voltaje de Alternador", size="3", font_weight="600"), align="center"),
                        rx.divider(margin_y="0.5rem", color="rgba(255, 255, 255, 0.05)"),
                        variable_range("Bajo", "180 - 210 V", "#FFB300"),
                        variable_range("Normal", "210 - 230 V", "#00FFAA"),
                        variable_range("Alto", "230 - 260 V", "#FF3366"),
                        style=glass_card_style,
                        width="100%",
                        align_items="start",
                        spacing="2"
                    ),
                    # Combustible
                    rx.vstack(
                        rx.hstack(rx.icon(tag="fuel", color="#B000FF", size=18), rx.heading("Combustible", size="3", font_weight="600"), align="center"),
                        rx.divider(margin_y="0.5rem", color="rgba(255, 255, 255, 0.05)"),
                        variable_range("Crítico", "0 - 10 %", "#FF3366"),
                        variable_range("Bajo", "5 - 25 %", "#FFB300"),
                        variable_range("Normal", "20 - 80 %", "#00FFAA"),
                        variable_range("Alto", "70 - 100 %", "#00E5FF"),
                        style=glass_card_style,
                        width="100%",
                        align_items="start",
                        spacing="2"
                    ),
                    # RPM
                    rx.vstack(
                        rx.hstack(rx.icon(tag="gauge", color="#FF6B35", size=18), rx.heading("Regulación RPM", size="3", font_weight="600"), align="center"),
                        rx.divider(margin_y="0.5rem", color="rgba(255, 255, 255, 0.05)"),
                        variable_range("Bajo", "1300 - 1450 RPM", "#FFB300"),
                        variable_range("Normal", "1450 - 1550 RPM", "#00FFAA"),
                        variable_range("Alto", "1550 - 1700 RPM", "#FF3366"),
                        style=glass_card_style,
                        width="100%",
                        align_items="start",
                        spacing="2"
                    ),
                    columns=rx.breakpoints(initial="1", md="2"),
                    spacing="4",
                    width="100%",
                    margin_top="1rem"
                ),
                value="variables"
            ),
            width="100%",
            margin_top="1.5rem",
            defaultValue="rules",
        ),
        width="100%",
        spacing="4",
        align_items="stretch"
    )

def configuracion() -> rx.Component:
    """Página de configuración."""
    return template(config_content())
