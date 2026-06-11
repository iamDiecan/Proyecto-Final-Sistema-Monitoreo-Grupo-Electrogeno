# sigen-frontend/sigen/pages/admin.py
import reflex as rx
from sigen.templates.template import template
from sigen.styles import CARD_BG, CARD_BORDER, TEXT_COLOR, MUTED_TEXT
from sigen.state.admin_state import AdminState

def user_row(user: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(user["username"]),
        rx.table.cell(rx.badge(user["role"], color_scheme=rx.cond(user["role"] == "Admin", "red", "blue"))),
        rx.table.cell(rx.button("Editar", size="1", variant="soft")),
    )

def admin() -> rx.Component:
    """Página de Administración (Gestión de Usuarios y Backups)."""
    return template(
        rx.vstack(
            rx.heading("Panel de Administración", size="8", margin_bottom="1rem", color=TEXT_COLOR),
            rx.text("Gestión de usuarios y configuración global del sistema.", color=MUTED_TEXT, margin_bottom="2rem"),
            
            rx.grid(
                # Card de Usuarios
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.icon(tag="users", size=24, color="#3B82F6"),
                            rx.heading("Gestión de Usuarios", size="5", color=TEXT_COLOR),
                            spacing="2",
                            align="center"
                        ),
                        rx.divider(margin_y="1rem"),
                        rx.text("Lista de usuarios registrados:", size="2", color=MUTED_TEXT, margin_bottom="1rem"),
                        
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Usuario"),
                                    rx.table.column_header_cell("Rol"),
                                    rx.table.column_header_cell("Acciones"),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(AdminState.users, user_row)
                            ),
                            variant="surface",
                            size="2"
                        ),
                        
                        rx.dialog.root(
                            rx.dialog.trigger(
                                rx.button("Nuevo Usuario", margin_top="1rem", color_scheme="blue", variant="soft")
                            ),
                            rx.dialog.content(
                                rx.dialog.title("Registrar Nuevo Usuario"),
                                rx.dialog.description("Ingrese los datos del nuevo usuario."),
                                rx.vstack(
                                    rx.input(placeholder="Nombre de usuario", value=AdminState.new_username, on_change=AdminState.set_new_username),
                                    rx.input(placeholder="Email", value=AdminState.new_email, on_change=AdminState.set_new_email),
                                    rx.select(["Admin", "Operador", "Técnico"], value=AdminState.new_role, on_change=AdminState.set_new_role),
                                    rx.input(placeholder="Contraseña", type="password", value=AdminState.new_password, on_change=AdminState.set_new_password),
                                    spacing="3"
                                ),
                                rx.hstack(
                                    rx.dialog.close(rx.button("Cancelar", variant="soft", color_scheme="gray")),
                                    rx.dialog.close(rx.button("Guardar", on_click=AdminState.save_user)),
                                    spacing="3",
                                    margin_top="16px",
                                    justify="end"
                                )
                            )
                        ),
                        
                        align="start"
                    ),
                    background=CARD_BG,
                    border=CARD_BORDER,
                    padding="2rem",
                    border_radius="16px",
                ),
                
                # Card de Backups
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.icon(tag="database-backup", size=24, color="#10B981"),
                            rx.heading("Copias de Seguridad", size="5", color=TEXT_COLOR),
                            spacing="2",
                            align="center"
                        ),
                        rx.divider(margin_y="1rem"),
                        rx.text("Backups diarios automatizados (SQLite + InfluxDB).", size="2", color=MUTED_TEXT),
                        rx.hstack(
                            rx.badge("Servicio Activo", color_scheme="green"),
                            rx.text(AdminState.last_backup_time, size="1", color=MUTED_TEXT),
                            spacing="2",
                            margin_y="1rem",
                            align="center"
                        ),
                        rx.button(
                            "Forzar Backup Ahora", 
                            icon="download", 
                            color_scheme="green", 
                            variant="solid",
                            loading=AdminState.is_backing_up,
                            on_click=AdminState.force_backup
                        ),
                        align="start"
                    ),
                    background=CARD_BG,
                    border=CARD_BORDER,
                    padding="2rem",
                    border_radius="16px",
                ),
                
                columns="2",
                spacing="4",
                width="100%"
            )
        )
    )
