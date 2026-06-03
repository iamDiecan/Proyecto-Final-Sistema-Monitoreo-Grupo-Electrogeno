# sigen/sigen.py
import reflex as rx

# Importar todas las páginas y componentes
from sigen.pages.dashboard import dashboard
from sigen.pages.alertas import alertas
from sigen.pages.configuracion import configuracion
from sigen.pages.generador_detail import generador_detail
from sigen.state.generador_state import GeneradorState
from sigen.styles import global_style, glass_card_style, ACCENT_CYAN, MUTED_TEXT

def index() -> rx.Component:
    """Página de inicio / Splash de entrada a SIGEGEN."""
    return rx.center(
        rx.vstack(
            rx.center(
                rx.icon(tag="activity", size=48, color=ACCENT_CYAN),
                background=f"{ACCENT_CYAN}15",
                padding="20px",
                border_radius="24px",
                margin_bottom="1rem"
            ),
            rx.heading("SIGEGEN v2.0", size="9", font_weight="800", letter_spacing="0.05em"),
            rx.heading(
                "Sistema Inteligente de Gestión y Monitoreo de Grupos Electrógenos",
                size="4",
                font_weight="500",
                color=MUTED_TEXT,
                text_align="center",
                max_width="600px"
            ),
            rx.divider(color="rgba(255, 255, 255, 0.05)", margin_y="1.5rem"),
            rx.text(
                "Monitoreo de telemetría por lógica difusa y analítica en tiempo real para la provincia de Formosa.",
                size="3",
                color=MUTED_TEXT,
                text_align="center",
                max_width="500px"
            ),
            rx.hstack(
                rx.button(
                    "Ingresar al Panel",
                    on_click=lambda: rx.redirect("/dashboard"),
                    color_scheme="indigo",
                    size="4",
                    cursor="pointer",
                    padding="0 2rem",
                    height="48px",
                    border_radius="12px"
                ),
                rx.button(
                    "Ver Alertas",
                    on_click=lambda: rx.redirect("/alertas"),
                    variant="outline",
                    color_scheme="gray",
                    size="4",
                    cursor="pointer",
                    padding="0 2rem",
                    height="48px",
                    border_radius="12px"
                ),
                spacing="4",
                margin_top="2rem"
            ),
            spacing="4",
            align="center",
            style=glass_card_style,
            padding="3.5rem",
            max_width="700px"
        ),
        min_height="100vh",
        width="100vw",
        background="radial-gradient(circle at top, #1E1B4B 0%, #0A0D1A 100%)",
        padding="2rem"
    )

# Crear la aplicación con los estilos globales cargados
app = rx.App(style=global_style)

# Registrar páginas con on_load handlers para poblar estados
app.add_page(index, route="/", title="SIGEGEN - Inicio")
app.add_page(dashboard, route="/dashboard", title="SIGEGEN - Dashboard", on_load=GeneradorState.cargar_todos_datos)
app.add_page(alertas, route="/alertas", title="SIGEGEN - Historial de Alertas", on_load=GeneradorState.cargar_alertas)
app.add_page(configuracion, route="/configuracion", title="SIGEGEN - Parámetros y Configuración")
app.add_page(generador_detail, route="/generador/[id]", title="SIGEGEN - Detalle de Generador", on_load=GeneradorState.cargar_detalle_por_id)