# sigen-backend/config.py
"""
Configuración centralizada del backend SIGEGEN.
Carga variables de entorno desde el archivo .env ubicado en la raíz del proyecto.
"""
import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Cargar .env desde la raíz del proyecto (un nivel arriba de sigen-backend/)
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ENV_PATH = os.path.join(_BASE_DIR, ".env")
load_dotenv(_ENV_PATH)


@dataclass(frozen=True)
class Settings:
    """Parámetros de configuración inmutables cargados una sola vez al inicio."""

    # ── InfluxDB ─────────────────────────────────────────────
    influxdb_url: str = os.getenv("INFLUXDB_URL", "http://localhost:8086")
    influxdb_token: str = os.getenv("INFLUXDB_TOKEN", "")
    influxdb_org: str = os.getenv("INFLUXDB_ORG", "sigegen")
    influxdb_bucket: str = os.getenv("INFLUXDB_BUCKET", "generadores")
    influxdb_timeout_ms: int = int(os.getenv("INFLUXDB_TIMEOUT_MS", "5000"))

    # ── MQTT ─────────────────────────────────────────────────
    mqtt_broker: str = os.getenv("MQTT_BROKER", "localhost")
    mqtt_port: int = int(os.getenv("MQTT_PORT", "1883"))
    mqtt_username: str = os.getenv("MQTT_USERNAME", "")
    mqtt_password: str = os.getenv("MQTT_PASSWORD", "")
    mqtt_topic: str = os.getenv("MQTT_TOPIC", "sigegen/+/+/datos")
    mqtt_qos: int = int(os.getenv("MQTT_QOS", "1"))

    # ── SQLite (fallback) ────────────────────────────────────
    sqlite_db_path: str = os.getenv(
        "SQLITE_DB_PATH",
        os.path.join(_BASE_DIR, "sigegen.db"),
    )

    # ── Backend ──────────────────────────────────────────────
    backend_port: int = int(os.getenv("BACKEND_PORT", "8001"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # ── Cache ────────────────────────────────────────────────
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", "60"))
    cache_max_size: int = int(os.getenv("CACHE_MAX_SIZE", "128"))


# Singleton ──────────────────────────────────────────────────
_settings_instance: Settings | None = None


def get_settings() -> Settings:
    """Retorna la instancia única de Settings (lazy singleton)."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
