# sigen-frontend/sigen/components/digital_twin.py
import reflex as rx
from sigen.styles import CARD_BG, CARD_BORDER, MUTED_TEXT, TEXT_COLOR

def digital_twin(estado: str, temp: float, rpm: float, voltaje: float, combustible: float) -> rx.Component:
    """Gemelo Digital 2D con animaciones e indicadores integrados."""
    
    # Colores base según estado
    primary_color = rx.cond(
        estado == "normal", "#10B981",
        rx.cond(estado == "precaucion", "#F59E0B",
        rx.cond(estado == "alerta", "#F97316", "#EF4444"))
    )
    
    # Velocidad de animación estática por ahora para evitar problemas de tipos con rx.Var
    anim_duration = "1s"
    
    svg_element = rx.el.svg(
        # Chasis Base
        rx.el.rect(x="20", y="50", width="360", height="150", rx_="15", fill="#1E293B", stroke="rgba(255,255,255,0.1)", stroke_width="2"),
        
        # Panel de Control
        rx.el.rect(x="280", y="70", width="80", height="110", rx_="5", fill="#0F172A", stroke="rgba(255,255,255,0.05)", stroke_width="1"),
        rx.el.circle(cx="320", cy="100", r="15", fill="#10B981"),
        rx.el.text("ON", x="320", y="105", fill="white", font_size="10", text_anchor="middle", font_family="sans-serif"),
        
        # Indicador Digital de Voltaje
        rx.el.rect(x="290", y="130", width="60", height="25", rx_="3", fill="#000"),
        rx.el.text(voltaje.to(str) + "V", x="320", y="147", fill=primary_color, font_size="12", font_family="monospace", text_anchor="middle", font_weight="bold"),
        
        # Motor Principal
        rx.el.rect(x="150", y="80", width="100", height="90", rx_="10", fill="#334155"),
        rx.el.path(d="M 150 100 L 250 100 M 150 120 L 250 120 M 150 140 L 250 140", stroke="#1E293B", stroke_width="4"),
        
        # Radiador y Ventilador
        rx.el.rect(x="40", y="70", width="80", height="110", rx_="5", fill="#0F172A"),
        rx.el.g(
            rx.el.circle(cx="80", cy="125", r="35", fill="none", stroke="#475569", stroke_width="2"),
            rx.el.path(d="M 80 90 L 80 160 M 45 125 L 115 125 M 55 100 L 105 150 M 55 150 L 105 100", stroke="#94A3B8", stroke_width="4"),
            style={"transformOrigin": "80px 125px", "animation": f"spin {anim_duration} linear infinite"}
        ),
        
        # Tanque de Combustible
        rx.el.rect(x="40", y="210", width="320", height="20", rx_="5", fill="#0F172A"),
        rx.el.rect(
            x="40", y="210", 
            width=(combustible.to(float) * 3.2).to(str), 
            height="20", rx_="5", fill=primary_color, opacity="0.8"
        ),
        rx.el.text(combustible.to(str) + "% Combustible", x="200", y="224", fill="white", font_size="10", font_family="sans-serif", text_anchor="middle"),
        
        view_box="0 0 400 250",
        width="100%",
        style={
            "@keyframes spin": {"100%": {"transform": "rotate(360deg)"}}
        }
    )
    
    return rx.box(
        rx.box(
            svg_element,
            style={"position": "relative", "width": "100%", "maxWidth": "500px", "margin": "0 auto", "padding": "2rem"}
        ),
        background=CARD_BG,
        border=CARD_BORDER,
        border_radius="16px",
        width="100%",
        padding="1rem",
        box_shadow="inset 0 2px 10px rgba(0,0,0,0.2)"
    )
