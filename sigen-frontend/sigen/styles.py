# sigen/styles.py
import reflex as rx

# Paleta de colores e identidades
BG_COLOR = "#0A0D1A"         # Fondo principal de la app
CARD_BG = "rgba(22, 28, 45, 0.7)" # Fondo de tarjeta (Glassmorphism)
CARD_BORDER = "1px solid rgba(255, 255, 255, 0.08)"
SIDEBAR_BG = "#0D1122"       # Fondo de la barra lateral
ACCENT_COLOR = "#4F46E5"     # Indigo
ACCENT_CYAN = "#06B6D4"      # Cyan
TEXT_COLOR = "#E2E8F0"       # Gris claro para legibilidad
MUTED_TEXT = "#94A3B8"       # Gris muted

# Estados de alerta
STATE_COLORS = {
    "normal": "#10B981",       # Esmeralda
    "precaucion": "#F59E0B",   # Ámbar
    "alerta": "#F97316",       # Naranja
    "falla": "#EF4444",        # Rojo
    "emergencia": "#EF4444"    # Rojo
}

STATE_BG = {
    "normal": "rgba(16, 185, 129, 0.15)",
    "precaucion": "rgba(245, 158, 11, 0.15)",
    "alerta": "rgba(249, 115, 22, 0.15)",
    "falla": "rgba(239, 68, 68, 0.15)",
    "emergencia": "rgba(239, 68, 68, 0.15)"
}

# Estilo global de tarjeta con blur
glass_card_style = dict(
    background=CARD_BG,
    border=CARD_BORDER,
    backdrop_filter="blur(12px)",
    border_radius="16px",
    padding="1.5rem",
    box_shadow="0 8px 32px 0 rgba(0, 0, 0, 0.3)",
)

# Estilos globales para la app
global_style = {
    "body": {
        "background_color": BG_COLOR,
        "color": TEXT_COLOR,
        "font_family": "'Outfit', 'Inter', sans-serif",
    },
    rx.heading: {
        "color": TEXT_COLOR,
        "font_weight": "600",
    },
    rx.text: {
        "color": TEXT_COLOR,
    }
}