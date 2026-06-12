# sigen/sigen.py
import reflex as rx

# Importar todas las páginas y componentes
from sigen.pages.dashboard import dashboard
from sigen.pages.alertas import alertas
from sigen.pages.configuracion import configuracion
from sigen.pages.generador_detail import generador_detail
from sigen.state.generador_state import GeneradorState
from sigen.styles import global_style, glass_card_style, ACCENT_CYAN, MUTED_TEXT

from sigen.pages.login import login
from sigen.pages.admin import admin
from sigen.pages.maintenance import maintenance
from sigen.pages.alerts_center import alerts_center
from sigen.pages.map import map_page
from sigen.pages.kpi import kpi
from sigen.pages.telegram import telegram
from sigen.pages.reportes import reportes

from sigen.state.maintenance_state import MaintenanceState
from sigen.state.alert_state import AlertState
from sigen.state.map_state import MapState
from sigen.state.kpi_state import KpiState
from sigen.state.admin_state import AdminState
from sigen.state.telegram_state import TelegramState

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

from sigen.state.auth_state import AuthState

# Crear la aplicación con los estilos globales cargados
app = rx.App(style=global_style)

# ── Páginas Base (v2 y v3) ───────────────────────────
from sigen.pages.inicio import inicio

app.add_page(inicio, route="/", title="SIGEGEN - Inicio", image="/favicon.ico")
app.add_page(dashboard, route="/dashboard", title="SIGEGEN - Dashboard Operativo")
app.add_page(generador_detail, route="/nodo/[nodo_id]", title="SIGEGEN - Detalle")
app.add_page(alertas, route="/alertas_legacy", title="SIGEGEN - Alertas (Legacy)")
app.add_page(configuracion, route="/configuracion", title="SIGEGEN - Configuración")

# ── Páginas Nuevas (v3.0) ─────────────────────────
app.add_page(login, route="/login", title="SIGEGEN - Iniciar Sesión")
app.add_page(admin, route="/admin", title="SIGEGEN - Administración")
app.add_page(maintenance, route="/maintenance", title="SIGEGEN - Mantenimiento", on_load=MaintenanceState.fetch_records)
app.add_page(alerts_center, route="/alertas", title="SIGEGEN - Centro de Alertas", on_load=AlertState.fetch_alerts)
app.add_page(map_page, route="/map", title="SIGEGEN - Mapa Provincial", on_load=MapState.fetch_nodes)
app.add_page(kpi, route="/kpi", title="SIGEGEN - KPIs Operativos", on_load=KpiState.fetch_kpi)
app.add_page(generador_detail, route="/generador/[id]", title="SIGEGEN - Detalle de Generador", on_load=GeneradorState.cargar_detalle_por_id)
app.add_page(telegram, route="/telegram", title="SIGEGEN - Telegram Bot")
app.add_page(reportes, route="/reportes", title="SIGEGEN - Reportes")