# sigen-frontend/sigen/pages/maintenance.py
import reflex as rx
from typing import List, Dict, Any
from sigen.templates.template import template
from sigen.styles import CARD_BG, CARD_BORDER, TEXT_COLOR, MUTED_TEXT
from sigen.state.maintenance_state import MaintenanceState

def record_row(record: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(record["nodo"].to(str), font_weight="bold"),
        rx.table.cell(record["fecha"].to(str)),
        rx.table.cell(rx.badge(record["tipo"].to(str), color_scheme="blue")),
        rx.table.cell(record["tecnico"].to(str)),
        rx.table.cell(record["horas"].to(str) + " h"),
    )

def maintenance() -> rx.Component:
    """Gestión de Mantenimiento Predictivo."""
    return template(
        rx.vstack(
            rx.heading("Mantenimiento Predictivo", size="8", margin_bottom="1rem", color=TEXT_COLOR),
            rx.text("Historial y predicción de servicios a los grupos electrógenos.", color=MUTED_TEXT, margin_bottom="2rem"),
            
            rx.box(
                rx.hstack(
                    rx.heading("Historial de Servicios", size="5", color=TEXT_COLOR),
                    rx.spacer(),
                    rx.link(
                        rx.button(
                            rx.icon(tag="file-spreadsheet", size=16),
                            "Descargar Reporte (Excel)",
                            color_scheme="green",
                            variant="solid",
                            cursor="pointer"
                        ),
                        href="http://localhost:8002/api/reportes/excel",
                        is_external=True
                    ),
                    rx.dialog.root(
                        rx.dialog.trigger(
                            rx.button("Registrar Servicio", icon="plus", color_scheme="indigo", variant="soft")
                        ),
                        rx.dialog.content(
                            rx.dialog.title("Registrar Nuevo Servicio"),
                            rx.dialog.description("Ingrese los datos del mantenimiento realizado."),
                            rx.vstack(
                                rx.input(placeholder="Nodo (ej. nodo_01)", value=MaintenanceState.form_nodo, on_change=MaintenanceState.set_form_nodo),
                                rx.input(placeholder="Fecha (YYYY-MM-DD)", type="date", value=MaintenanceState.form_fecha, on_change=MaintenanceState.set_form_fecha),
                                rx.select(["Preventivo", "Correctivo", "Inspección"], value=MaintenanceState.form_tipo, on_change=MaintenanceState.set_form_tipo),
                                rx.input(placeholder="Técnico", value=MaintenanceState.form_tecnico, on_change=MaintenanceState.set_form_tecnico),
                                rx.input(placeholder="Horas Motor", value=MaintenanceState.form_horas, on_change=MaintenanceState.set_form_horas),
                                rx.text_area(placeholder="Observaciones", value=MaintenanceState.form_obs, on_change=MaintenanceState.set_form_obs),
                                spacing="3"
                            ),
                            rx.hstack(
                                rx.dialog.close(rx.button("Cancelar", variant="soft", color_scheme="gray")),
                                rx.dialog.close(rx.button("Guardar", on_click=MaintenanceState.save_mock_record)),
                                spacing="3",
                                margin_top="16px",
                                justify="end"
                            )
                        )
                    ),
                    width="100%",
                    align="center",
                    margin_bottom="1rem"
                ),
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Nodo"),
                            rx.table.column_header_cell("Fecha"),
                            rx.table.column_header_cell("Tipo"),
                            rx.table.column_header_cell("Técnico"),
                            rx.table.column_header_cell("Horas Motor"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(MaintenanceState.records, record_row)
                    ),
                    variant="surface",
                    size="2",
                    width="100%"
                ),
                background=CARD_BG,
                border=CARD_BORDER,
                padding="1.5rem",
                border_radius="16px",
                width="100%"
            )
        )
    )
