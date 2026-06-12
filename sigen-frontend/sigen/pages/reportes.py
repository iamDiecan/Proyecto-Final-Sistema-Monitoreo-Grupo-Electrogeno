# sigen-frontend/sigen/pages/reportes.py
import reflex as rx
from sigen.templates.template import template
from sigen.styles import CARD_BG, CARD_BORDER, TEXT_COLOR, MUTED_TEXT

def mock_report_row(data: list) -> rx.Component:
    return rx.table.row(
        rx.table.cell(data[0]),
        rx.table.cell(data[1]),
        rx.table.cell(data[2]),
        rx.table.cell(data[3]),
        rx.table.cell(data[4]),
    )

def reportes() -> rx.Component:
    """Generación de Reportes."""
    mock_data = [
        ["2023-10-01", "nodo_01", "220V", "1500 RPM", "Normal"],
        ["2023-10-02", "nodo_02", "218V", "1490 RPM", "Alerta"],
        ["2023-10-03", "nodo_01", "221V", "1505 RPM", "Normal"],
        ["2023-10-04", "nodo_03", "0V", "0 RPM", "Offline"],
    ]

    return template(
        rx.vstack(
            rx.heading("Reportes y Exportación", size="8", margin_bottom="1rem", color=TEXT_COLOR),
            rx.text("Genere reportes históricos en formato PDF o Excel.", color=MUTED_TEXT, margin_bottom="2rem"),
            
            rx.box(
                rx.grid(
                    rx.vstack(
                        rx.text("Fecha Inicio", size="2", color=MUTED_TEXT),
                        rx.input(type="date", width="100%")
                    ),
                    rx.vstack(
                        rx.text("Fecha Fin", size="2", color=MUTED_TEXT),
                        rx.input(type="date", width="100%")
                    ),
                    rx.vstack(
                        rx.text("Nodo", size="2", color=MUTED_TEXT),
                        rx.select(["Todos", "nodo_01", "nodo_02", "nodo_03"], width="100%", default_value="Todos")
                    ),
                    rx.vstack(
                        rx.text("Acciones", size="2", color=MUTED_TEXT),
                        rx.hstack(
                            rx.button("PDF", icon="file-text", color_scheme="red", flex="1"),
                            rx.button("Excel", icon="file-spreadsheet", color_scheme="green", flex="1"),
                            width="100%",
                            spacing="2"
                        ),
                        width="100%"
                    ),
                    columns="4",
                    spacing="4",
                    width="100%",
                ),
                background=CARD_BG,
                border=CARD_BORDER,
                padding="1.5rem",
                border_radius="16px",
                width="100%",
                margin_bottom="2rem"
            ),
            
            rx.box(
                rx.heading("Vista Previa de Datos", size="4", margin_bottom="1rem", color=TEXT_COLOR),
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Fecha"),
                            rx.table.column_header_cell("Nodo"),
                            rx.table.column_header_cell("Tensión Media"),
                            rx.table.column_header_cell("RPM Media"),
                            rx.table.column_header_cell("Estado General"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(mock_data, mock_report_row)
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
