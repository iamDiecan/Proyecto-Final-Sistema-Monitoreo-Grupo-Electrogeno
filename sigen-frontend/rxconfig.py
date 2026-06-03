# rxconfig.py
import reflex as rx

config = rx.Config(
    app_name="sigen",
    db_url="sqlite:///reflex.db",
    telemetry_enabled=False,
    # No especifiques api_url, usa el puerto por defecto 8000
)
