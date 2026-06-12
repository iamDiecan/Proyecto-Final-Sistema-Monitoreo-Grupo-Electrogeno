# sigen/components/charts.py
import reflex as rx
from typing import List, Dict, Any

def telemetry_chart(data: List[Dict[str, Any]], data_key: str, stroke_color: str, fill_color: str) -> rx.Component:
    """Gráfico de área para representar series de tiempo de telemetría."""
    return rx.box(
        rx.recharts.responsive_container(
            rx.recharts.area_chart(
                rx.recharts.area(
                    data_key=data_key,
                    stroke=stroke_color,
                    fill=fill_color,
                    type_="monotone",
                    stroke_width=2,
                ),
                rx.recharts.x_axis(
                    data_key="hora",
                    stroke="#64748B",
                    font_size=11,
                    tick_line=False,
                ),
                rx.recharts.y_axis(
                    stroke="#64748B",
                    font_size=11,
                    tick_line=False,
                    domain=["auto", "auto"]
                ),
                rx.recharts.cartesian_grid(
                    stroke_dasharray="3 3",
                    stroke="rgba(255, 255, 255, 0.04)"
                ),
                rx.recharts.tooltip(),
                data=data,
                margin={"top": 5, "right": 5, "left": -20, "bottom": 5},
            ),
            height=250,
            width="100%"
        ),
        width="100%",
        padding_top="1rem"
    )