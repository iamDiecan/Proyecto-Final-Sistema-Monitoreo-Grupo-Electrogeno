# sigen/pages/configuracion.py
import reflex as rx
from sigen.templates.template import template
from sigen.styles import MUTED_TEXT, glass_card_style, TEXT_COLOR

def rule_row(rule_num: int, condition: str, action: str, level: str) -> rx.Component:
    """Una fila representando una regla difusa."""
    color = "#10B981" if "normal" in level else "#EF4444" if "critico" in level or "emergencia" in level else "#F97316"
    return rx.hstack(
        rx.badge(f"R{rule_num}", color_scheme="indigo", font_weight="600"),
        rx.text("SI", color=MUTED_TEXT, font_weight="600"),
        rx.text(condition, color=TEXT_COLOR, font_weight="500"),
        rx.text("ENTONCES", color=MUTED_TEXT, font_weight="600"),
        rx.badge(action.upper(), color_scheme="red" if color == "#EF4444" else "orange" if color == "#F97316" else "green", font_weight="600"),
        spacing="3",
        align="center",
        padding="0.75rem 1rem",
        border_bottom="1px solid rgba(255, 255, 255, 0.03)",
        width="100%"
    )

def config_content() -> rx.Component:
    """Contenido del panel de configuración."""
    return rx.vstack(
        # Título y Subtítulo
        rx.vstack(
            rx.heading("Parámetros del Sistema y Lógica Difusa", size="8", font_weight="700"),
            rx.text("Descripción matemática de las funciones de pertenencia y reglas de inferencia", size="3", color=MUTED_TEXT),
            align_items="start",
            spacing="1"
        ),
        
        # Tabs de Configuración
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("Reglas Difusas (Inferencia)", value="rules"),
                rx.tabs.trigger("Variables de Entrada", value="variables"),
            ),
            
            # Tab 1: Reglas de Inferencia
            rx.tabs.content(
                rx.vstack(
                    rx.heading("Reglas de Control de Alertas (12 Reglas)", size="4", font_weight="600", margin_bottom="1rem"),
                    rx.vstack(
                        rule_row(1, "Temperatura del Motor es CRÍTICA", "Alerta es EMERGENCIA", "emergencia"),
                        rule_row(2, "Temperatura es ALTA Y Voltaje es BAJO", "Alerta es CRÍTICO", "critico"),
                        rule_row(3, "Temperatura es ALTA Y Vibración es ALTA", "Alerta es CRÍTICO", "critico"),
                        rule_row(4, "Combustible es CRÍTICO", "Alerta es EMERGENCIA", "emergencia"),
                        rule_row(5, "Combustible es BAJO Y RPM es ANORMAL", "Alerta es ALERTA", "alerta"),
                        rule_row(6, "Combustible es BAJO Y Temperatura es NORMAL", "Alerta es PRECAUCIÓN", "precaucion"),
                        rule_row(7, "RPM es BAJO O RPM es ALTO", "Alerta es PRECAUCIÓN", "precaucion"),
                        rule_row(8, "RPM es ALTO Y Vibración es ALTA", "Alerta es CRÍTICO", "critico"),
                        rule_row(9, "Frecuencia está FUERA DE RANGO", "Alerta es ALERTA", "alerta"),
                        rule_row(10, "Voltaje es ALTO Y Frecuencia es ALTA (Sobrecarga)", "Alerta es CRÍTICO", "critico"),
                        rule_row(11, "Todas las variables están en niveles NORMALES", "Alerta es NORMAL", "normal"),
                        rule_row(12, "Temperatura es ALTA Y Combustible es BAJO", "Alerta es CRÍTICO", "critico"),
                        spacing="1",
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
                        rx.heading("Temperatura del Motor", size="3", font_weight="600"),
                        rx.text("• Baja: [0, 0, 50] °C", size="2"),
                        rx.text("• Normal: [40, 65, 90] °C", size="2"),
                        rx.text("• Alta: [80, 105, 120] °C", size="2"),
                        rx.text("• Crítica: [100, 115, 130, 130] °C", size="2"),
                        style=glass_card_style,
                        width="100%",
                        align_items="start",
                        spacing="2"
                    ),
                    # Voltaje
                    rx.vstack(
                        rx.heading("Voltaje de Alternador", size="3", font_weight="600"),
                        rx.text("• Bajo: [180, 195, 210] V", size="2"),
                        rx.text("• Normal: [210, 220, 230] V", size="2"),
                        rx.text("• Alto: [230, 245, 260] V", size="2"),
                        style=glass_card_style,
                        width="100%",
                        align_items="start",
                        spacing="2"
                    ),
                    # Combustible
                    rx.vstack(
                        rx.heading("Reserva de Combustible", size="3", font_weight="600"),
                        rx.text("• Crítico: [0, 0, 5, 10] %", size="2"),
                        rx.text("• Bajo: [5, 12, 25] %", size="2"),
                        rx.text("• Normal: [20, 50, 80] %", size="2"),
                        rx.text("• Alto: [70, 85, 100] %", size="2"),
                        style=glass_card_style,
                        width="100%",
                        align_items="start",
                        spacing="2"
                    ),
                    # RPM
                    rx.vstack(
                        rx.heading("Regulación RPM", size="3", font_weight="600"),
                        rx.text("• Bajo: [1300, 1400, 1450] RPM", size="2"),
                        rx.text("• Normal: [1450, 1500, 1550] RPM", size="2"),
                        rx.text("• Alto: [1550, 1600, 1700] RPM", size="2"),
                        style=glass_card_style,
                        width="100%",
                        align_items="start",
                        spacing="2"
                    ),
                    columns="2",
                    spacing="4",
                    width="100%",
                    margin_top="1rem"
                ),
                value="variables"
            ),
            width="100%",
            margin_top="1.5rem"
        ),
        width="100%",
        spacing="4",
        align_items="stretch"
    )

def configuracion() -> rx.Component:
    """Página de configuración."""
    return template(config_content())
