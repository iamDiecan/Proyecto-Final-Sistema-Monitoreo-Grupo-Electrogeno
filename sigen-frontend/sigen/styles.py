# sigen/styles.py
import reflex as rx

# ── Paleta de Colores SIGEGEN Ion ──
BG_COLOR = "#070B1A"         # Nocturno de subestación
CARD_BG = "#11162C"          # Azul voltaje bajo
TEXT_COLOR = "#EFF3FF"       # Blanco bobinado
MUTED_TEXT = "#8892B0"       # Gris ion

# ── Acentos y Estados ──
ACCENT_CYAN = "#00E5FF"      # Cian de arco eléctrico (Normalidad)
ACCENT_COLOR = ACCENT_CYAN   # Alias para componentes que usen ACCENT_COLOR
SIDEBAR_BG = "#0B0F19"       # Fondo para la barra lateral
STATUS_SUCCESS = "#00FFAA"   # Verde neón generador
STATUS_WARNING = "#FFB300"   # Ámbar chispa
STATUS_CRITICAL = "#FF1A1A"  # Rojo SCADA puro

# ── Parámetros Específicos ──
PARAM_OIL = MUTED_TEXT       # Neutro para reducir ruido visual
PARAM_TEMP = MUTED_TEXT      # Neutro
PARAM_FUEL = MUTED_TEXT      # Neutro

# Estados de alerta mapeados
STATE_COLORS = {
    "normal": STATUS_SUCCESS,
    "precaucion": STATUS_WARNING,
    "alerta": STATUS_WARNING,
    "falla": STATUS_CRITICAL,
    "emergencia": STATUS_CRITICAL
}

# ── Glow Effects ──
GLOW_CYAN = "0 0 15px rgba(0, 229, 255, 0.2)" # Resplandor atenuado
GLOW_CRITICAL = "0 0 20px rgba(255, 26, 26, 0.6)"
GLOW_FUEL = "0 0 15px rgba(136, 146, 176, 0.2)" # Neutro

CARD_BORDER = "1px solid rgba(136, 146, 176, 0.1)"

# Estilo global de tarjeta
glass_card_style = dict(
    background=CARD_BG,
    border=CARD_BORDER,
    border_radius="16px",
    padding="1.5rem",
    box_shadow="0 8px 32px 0 rgba(0, 0, 0, 0.3)",
    transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
    _hover={
        "box_shadow": "0 8px 32px 0 rgba(0, 0, 0, 0.4)",
        "border": f"1px solid {MUTED_TEXT}",
        "transform": "translateY(-2px)"
    }
)

# Estilos globales para la app
global_style = {
    "@keyframes scada-blink": {
        "0%": {"opacity": "1"},
        "50%": {"opacity": "0.3"},
        "100%": {"opacity": "1"},
    },
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