# sigen-frontend/sigen/pages/kpi.py
import reflex as rx
from sigen.templates.template import template
from sigen.styles import CARD_BG, CARD_BORDER, TEXT_COLOR, MUTED_TEXT
from sigen.state.kpi_state import KpiState

def kpi_card(title: str, value: rx.Var, trend: rx.Var, is_positive: rx.Var) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text(title, size="2", color=MUTED_TEXT, font_weight="500"),
            rx.heading(value, size="7", color=TEXT_COLOR),
            rx.hstack(
                rx.icon(
                    tag=rx.cond(is_positive, "trending-up", "trending-down"), 
                    size=14, 
                    color=rx.cond(is_positive, "#10B981", "#EF4444")
                ),
                rx.text(f"{trend} este mes", size="1", color=rx.cond(is_positive, "#10B981", "#EF4444")),
                align="center",
                spacing="1"
            ),
            align="start"
        ),
        background=CARD_BG,
        border=CARD_BORDER,
        padding="1.5rem",
        border_radius="16px",
        width="100%",
    )

def kpi() -> rx.Component:
    """Panel de Indicadores Clave de Rendimiento."""
    return template(
        rx.vstack(
            rx.heading("KPIs Operativos", size="8", margin_bottom="1rem", color=TEXT_COLOR),
            rx.text("Indicadores clave de rendimiento y eficiencia de la red.", color=MUTED_TEXT, margin_bottom="2rem"),
            
            rx.grid(
                kpi_card("Disponibilidad Global", f"{KpiState.data['disponibilidad']}%", KpiState.data["disponibilidad_trend"], KpiState.disp_positive),
                kpi_card("MTBF (Tiempo medio entre fallas)", f"{KpiState.data['mtbf_horas']} h", f"{KpiState.data['mtbf_trend']} h", KpiState.mtbf_positive),
                kpi_card("MTTR (Tiempo medio de reparación)", f"{KpiState.data['mttr_horas']} h", f"{KpiState.data['mttr_trend']} h", KpiState.mttr_positive),
                kpi_card("Consumo Promedio (L/h)", f"{KpiState.data['consumo_promedio_lh']}", KpiState.data["consumo_trend"], KpiState.consumo_positive),
                columns="4",
                spacing="4",
                width="100%"
            ),
            
            rx.grid(
                # Gráfico Disponibilidad
                rx.box(
                    rx.heading("Tendencia de Disponibilidad (%)", size="5", color=TEXT_COLOR, margin_bottom="1rem"),
                    rx.recharts.responsive_container(
                        rx.recharts.area_chart(
                            rx.recharts.area(
                                data_key="disponibilidad",
                                stroke="#10B981",
                                fill="rgba(16, 185, 129, 0.2)",
                                type_="monotone",
                                stroke_width=3,
                            ),
                            rx.recharts.x_axis(data_key="mes", stroke=MUTED_TEXT, font_size=12, tick_line=False),
                            rx.recharts.y_axis(stroke=MUTED_TEXT, font_size=12, tick_line=False, domain=["auto", "auto"]),
                            rx.recharts.cartesian_grid(stroke_dasharray="3 3", stroke="rgba(255,255,255,0.05)"),
                            rx.recharts.tooltip(),
                            data=KpiState.trend_data,
                            margin={"top": 10, "right": 10, "left": -20, "bottom": 0},
                        ),
                        height=300,
                        width="100%"
                    ),
                    background=CARD_BG,
                    border=CARD_BORDER,
                    padding="2rem",
                    border_radius="16px",
                    width="100%",
                ),
                
                # Gráfico Rendimiento
                rx.box(
                    rx.heading("Rendimiento Operativo (OEE)", size="5", color=TEXT_COLOR, margin_bottom="1rem"),
                    rx.recharts.responsive_container(
                        rx.recharts.bar_chart(
                            rx.recharts.bar(
                                data_key="rendimiento",
                                fill="#3B82F6",
                                radius=[4, 4, 0, 0]
                            ),
                            rx.recharts.x_axis(data_key="mes", stroke=MUTED_TEXT, font_size=12, tick_line=False),
                            rx.recharts.y_axis(stroke=MUTED_TEXT, font_size=12, tick_line=False, domain=["auto", "auto"]),
                            rx.recharts.cartesian_grid(stroke_dasharray="3 3", stroke="rgba(255,255,255,0.05)", vertical=False),
                            rx.recharts.tooltip(),
                            data=KpiState.trend_data,
                            margin={"top": 10, "right": 10, "left": -20, "bottom": 0},
                        ),
                        height=300,
                        width="100%"
                    ),
                    background=CARD_BG,
                    border=CARD_BORDER,
                    padding="2rem",
                    border_radius="16px",
                    width="100%",
                ),
                columns=rx.breakpoints(initial="1", md="2"),
                spacing="4",
                width="100%",
                margin_top="2rem"
            )
        )
    )
