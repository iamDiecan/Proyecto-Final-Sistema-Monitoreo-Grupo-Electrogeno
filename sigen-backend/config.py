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

    # ── App SQLite (CRUD: alertas, mantenimiento, usuarios) ──
    app_db_path: str = os.getenv(
        "APP_DB_PATH",
        os.path.join(_BASE_DIR, "sigen-backend", "sigegen_app.db"),
    )

    # ── Backend ──────────────────────────────────────────────
    backend_port: int = int(os.getenv("BACKEND_PORT", "8001"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # ── Cache ────────────────────────────────────────────────
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", "60"))
    cache_max_size: int = int(os.getenv("CACHE_MAX_SIZE", "128"))

    # ── Autenticación (JWT) ──────────────────────────────────
    jwt_secret: str = os.getenv("JWT_SECRET", "sigegen-secret-key-change-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "480"))

    # ── Watchdog de nodos ────────────────────────────────────
    watchdog_timeout_minutes: int = int(os.getenv("WATCHDOG_TIMEOUT_MINUTES", "5"))
    watchdog_check_interval_seconds: int = int(os.getenv("WATCHDOG_CHECK_INTERVAL_SECONDS", "60"))

    # ── Mantenimiento predictivo (horas) ─────────────────────
    maintenance_oil_change_hours: int = int(os.getenv("MAINTENANCE_OIL_CHANGE_HOURS", "250"))
    maintenance_filter_change_hours: int = int(os.getenv("MAINTENANCE_FILTER_CHANGE_HOURS", "500"))
    maintenance_inspection_hours: int = int(os.getenv("MAINTENANCE_INSPECTION_HOURS", "1000"))

    # ── Backups ──────────────────────────────────────────────
    backup_path: str = os.getenv(
        "BACKUP_PATH",
        os.path.join(_BASE_DIR, "backups"),
    )
    backup_retention_days: int = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))

    # ── Edge (Orange Pi) ─────────────────────────────────────
    edge_buffer_db_path: str = os.getenv(
        "EDGE_BUFFER_DB_PATH",
        os.path.join(_BASE_DIR, "edge_buffer.db"),
    )

    # ── Telegram Bot ─────────────────────────────────────────
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")


# Singleton ──────────────────────────────────────────────────
_settings_instance: Settings | None = None


def get_settings() -> Settings:
    """Retorna la instancia única de Settings (lazy singleton)."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
