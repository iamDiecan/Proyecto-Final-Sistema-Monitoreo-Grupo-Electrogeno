# rxconfig.py
import reflex as rx

config = rx.Config(
    app_name="sigen",
    db_url="sqlite:///reflex.db",
    telemetry_enabled=False,
    backend_port=8000,
    frontend_packages=[
        "recharts@2.12.7"
    ]
)
