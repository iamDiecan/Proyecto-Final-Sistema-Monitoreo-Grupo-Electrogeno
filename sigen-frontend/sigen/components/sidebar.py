# sigen/components/sidebar.py
import reflex as rx
from sigen.styles import SIDEBAR_BG, ACCENT_COLOR, TEXT_COLOR, MUTED_TEXT

def sidebar_item(label: str, icon_tag: str, url: str) -> rx.Component:
    """Un ítem de navegación individual para la barra lateral."""
    return rx.link(
        rx.hstack(
            rx.icon(tag=icon_tag, size=20, color=TEXT_COLOR),
            rx.text(label, size="3", font_weight="500", color=TEXT_COLOR),
            spacing="3",
            align="center",
            width="100%",
            padding="0.75rem 1rem",
            border_radius="10px",
            background=rx.cond(
                rx.State.router.page.path == url,
                "rgba(79, 70, 229, 0.2)",  # Color activo
                "transparent"
            ),
            border_left=rx.cond(
                rx.State.router.page.path == url,
                f"3px solid {ACCENT_COLOR}",
                "3px solid transparent"
            ),
            _hover={
                "background": "rgba(255, 255, 255, 0.05)",
                "transition": "all 0.2s ease-in-out"
            }
        ),
        href=url,
        text_decoration="none",
        width="100%"
    )

def sidebar() -> rx.Component:
    """La barra lateral de navegación principal."""
    return rx.vstack(
        # Logo y Cabecera
        rx.hstack(
            rx.icon(tag="activity", size=28, color="#06B6D4"),
            rx.vstack(
                rx.heading("SIGEGEN", size="4", font_weight="700", letter_spacing="0.05em"),
                rx.text("Monitoreo Inteligente", size="1", color=MUTED_TEXT, margin_top="-4px"),
                spacing="0"
            ),
            spacing="3",
            padding="1.5rem 1rem",
            align="center",
            width="100%",
            border_bottom="1px solid rgba(255, 255, 255, 0.05)"
        ),
        
        # Enlaces de navegación
        rx.vstack(
            sidebar_item("Inicio", "home", "/"),
            sidebar_item("Dashboard", "layout-dashboard", "/dashboard"),
            sidebar_item("Historial de Alertas", "bell", "/alertas"),
            sidebar_item("Configuración", "settings", "/configuracion"),
            spacing="2",
            padding="1.5rem 0.75rem",
            width="100%",
            flex="1"
        ),
        
        # Pie de la barra lateral (Información del sistema)
        rx.vstack(
            rx.hstack(
                rx.badge("API Conectada", color_scheme="green", variant="solid"),
                rx.badge("v2.0", color_scheme="indigo", variant="outline"),
                spacing="2"
            ),
            rx.text("Provincia de Formosa", size="1", color=MUTED_TEXT),
            spacing="2",
            padding="1rem",
            width="100%",
            border_top="1px solid rgba(255, 255, 255, 0.05)",
            align="center"
        ),
        
        background=SIDEBAR_BG,
        width="260px",
        height="100vh",
        position="fixed",
        top="0",
        left="0",
        border_right="1px solid rgba(255, 255, 255, 0.05)",
        z_index="100"
    )
