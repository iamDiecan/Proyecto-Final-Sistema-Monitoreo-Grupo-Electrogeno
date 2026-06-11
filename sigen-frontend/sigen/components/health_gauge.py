# sigen-frontend/sigen/components/health_gauge.py
import reflex as rx
from sigen.styles import MUTED_TEXT

def health_gauge(score: rx.Var, size: int = 150) -> rx.Component:
    """Componente visual para mostrar el Health Score con un arco circular."""
    if not isinstance(score, rx.Var):
        score = rx.Var.create(score)
        
    # Determinamos el color basado en el score
    color = rx.cond(
        score >= 90,
        "#10B981",  # Verde - Excelente
        rx.cond(
            score >= 70,
            "#3B82F6",  # Azul - Bueno
            rx.cond(
                score >= 50,
                "#F59E0B",  # Amarillo - Advertencia
                "#EF4444"   # Rojo - Crítico
            )
        )
    )
    
    # Calcular stroke-dasharray para representar el porcentaje (longitud del círculo es ~283 para r=45)
    circumference = 283.0
    dash_offset = circumference - (score / 100.0) * circumference
    
    # Usar componentes nativos SVG de Reflex en lugar de rx.html
    svg_element = rx.el.svg(
        rx.el.circle(
            cx="50", cy="50", r="45", 
            fill="none", 
            stroke="rgba(255, 255, 255, 0.1)", 
            stroke_width="8"
        ),
        rx.el.circle(
            cx="50", cy="50", r="45", 
            fill="none", 
            stroke=color, 
            stroke_width="8",
            stroke_dasharray=str(circumference),
            stroke_dashoffset=dash_offset.to(str),
            stroke_linecap="round",
            transform="rotate(-90 50 50)",
            style={"transition": "stroke-dashoffset 1s ease-in-out, stroke 0.5s ease"}
        ),
        width=f"{size}", 
        height=f"{size}", 
        view_box="0 0 100 100"
    )
    
    return rx.box(
        rx.center(
            rx.box(
                svg_element,
                position="absolute"
            ),
            rx.vstack(
                rx.text(score.to_string(), size="7", font_weight="bold", color=color, line_height="1"),
                rx.text("Score", size="1", color=MUTED_TEXT, line_height="1"),
                align="center",
                spacing="1"
            ),
            width=f"{size}px",
            height=f"{size}px",
            position="relative"
        )
    )
