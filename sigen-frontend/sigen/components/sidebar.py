# sigen/components/sidebar.py
import reflex as rx
from sigen.styles import SIDEBAR_BG, ACCENT_COLOR, TEXT_COLOR, MUTED_TEXT

class SidebarState(rx.State):
    """Estado para el comportamiento del sidebar (especialmente en móviles)."""
    is_open: bool = False

    def toggle_sidebar(self):
        self.is_open = not self.is_open
        
    def set_is_open(self, value: bool):
        self.is_open = value

def sidebar_item(label: str, icon_tag: str, url: str) -> rx.Component:
    """Un ítem de navegación individual para la barra lateral."""
    return rx.link(
        rx.hstack(
            rx.icon(tag=icon_tag, size=18, color=TEXT_COLOR),
            rx.text(label, size="2", font_weight="500", color=TEXT_COLOR),
            spacing="3",
            align="center",
            width="100%",
            padding="0.6rem 1rem",
            border_radius="8px",
            background=rx.cond(
                rx.State.router.page.path == url,
                "rgba(255, 255, 255, 0.1)",  # Color activo neutral
                "transparent"
            ),
            border_left=rx.cond(
                rx.State.router.page.path == url,
                f"3px solid {TEXT_COLOR}",
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

def sidebar_section(title: str, icon_tag: str, items: list) -> rx.Component:
    """Una sección colapsable en la barra lateral."""
    return rx.accordion.item(
        header=rx.accordion.header(
            rx.hstack(
                rx.icon(tag=icon_tag, size=18, color=MUTED_TEXT),
                rx.text(title, size="2", font_weight="600", color=MUTED_TEXT, text_transform="uppercase", letter_spacing="0.05em"),
                spacing="2",
                align="center",
                width="100%",
            ),
            padding="0.5rem 0",
            background="transparent",
            _hover={"color": TEXT_COLOR}
        ),
        content=rx.accordion.content(
            rx.vstack(
                *items,
                spacing="1",
                width="100%",
                padding_left="1rem",
                border_left="1px solid rgba(255, 255, 255, 0.05)",
                margin_left="9px"
            )
        ),
        value=title,
        border_bottom="none",
        background="transparent"
    )

def sidebar_content() -> rx.Component:
    """El contenido principal de la barra lateral (logo, navegación y footer)."""
    return rx.vstack(
        # Logo y Cabecera
        rx.hstack(
            rx.icon(tag="activity", size=24, color=TEXT_COLOR),
            rx.vstack(
                rx.heading("SIGEGEN", size="4", font_weight="700", letter_spacing="0.05em"),
                rx.text("Industrial SCADA", size="1", color=MUTED_TEXT, margin_top="-4px"),
                spacing="0"
            ),
            spacing="3",
            padding="1.5rem 1rem",
            align="center",
            width="100%",
            border_bottom="1px solid rgba(255, 255, 255, 0.05)"
        ),
        
        # Enlaces de navegación con Acordeón
        rx.box(
            rx.vstack(
                sidebar_item("Inicio", "home", "/"),
                
                rx.accordion.root(
                    sidebar_section("Operaciones", "cpu", [
                        sidebar_item("Dashboard", "layout-dashboard", "/dashboard"),
                        sidebar_item("KPIs Operativos", "bar-chart-3", "/kpi"),
                        sidebar_item("Mapa Provincial", "map", "/map"),
                    ]),
                    sidebar_section("Gestión", "clipboard-list", [
                        sidebar_item("Mantenimiento", "wrench", "/maintenance"),
                        sidebar_item("Reportes", "file-text", "/reportes"),
                    ]),
                    sidebar_section("Automatización", "bot", [
                        sidebar_item("Alertas", "bell", "/alertas"),
                        sidebar_item("Telegram Bot", "send", "/telegram"),
                    ]),
                    sidebar_section("Administración", "shield", [
                        sidebar_item("Configuración", "settings", "/configuracion"),
                        sidebar_item("Usuarios", "users", "/admin"),
                    ]),
                    type="multiple",
                    defaultValue=["Operaciones", "Gestión"],
                    width="100%",
                    variant="ghost",
                    background="transparent"
                ),
                spacing="2",
                width="100%",
            ),
            padding="1rem 0.75rem",
            width="100%",
            flex="1",
            overflow_y="auto"
        ),
        
        # Pie de la barra lateral
        rx.vstack(
            rx.hstack(
                rx.badge("API Conectada", color_scheme="green", variant="solid"),
                rx.badge("v3.0", color_scheme="indigo", variant="outline"),
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
        display="flex",
        flex_direction="column"
    )

def sidebar() -> rx.Component:
    """Componente de barra lateral oculto (Drawer) en todas las pantallas."""
    return rx.drawer.root(
        rx.drawer.overlay(z_index="100"),
        rx.drawer.portal(
            rx.drawer.content(
                rx.drawer.title("Menú de Navegación", display="none"),
                rx.drawer.description("Opciones de navegación del sistema", display="none"),
                sidebar_content(),
                background=SIDEBAR_BG,
                width="260px",
                height="100vh",
                position="fixed",
                top="0",
                left="0",
                z_index="101"
            )
        ),
        direction="left",
        open=SidebarState.is_open,
        on_open_change=SidebarState.set_is_open,
    )
