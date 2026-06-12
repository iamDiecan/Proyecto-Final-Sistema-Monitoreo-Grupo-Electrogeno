# sigen-backend/models/database.py
"""
Modelos SQLModel para SIGEGEN v3.0
Base de datos relacional para: Usuarios, Alertas, Mantenimiento, Configuración de Nodos.
La telemetría time-series sigue en InfluxDB.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional, Generator
from enum import Enum

from sqlmodel import SQLModel, Field, Session, create_engine

from config import get_settings

logger = logging.getLogger("sigegen.models")


# ── Enumeraciones ────────────────────────────────────────────

class UserRole(str, Enum):
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    TECNICO = "tecnico"


class AlertLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertStatus(str, Enum):
    ACTIVE = "active"
    READ = "read"
    RESOLVED = "resolved"


# ── Modelos ──────────────────────────────────────────────────

class User(SQLModel, table=True):
    """Usuario del sistema con rol de acceso."""
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, max_length=50)
    password_hash: str = Field(max_length=255)
    email: str = Field(default="", max_length=100)
    full_name: str = Field(default="", max_length=100)
    role: str = Field(default=UserRole.TECNICO.value, max_length=20)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(default=None)


class Alert(SQLModel, table=True):
    """Alerta generada por el sistema de detección."""
    __tablename__ = "alerts"

    id: Optional[int] = Field(default=None, primary_key=True)
    node_id: str = Field(index=True, max_length=20)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    level: str = Field(max_length=10)  # INFO, WARNING, CRITICAL
    status: str = Field(default=AlertStatus.ACTIVE.value, max_length=10)
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    source: str = Field(default="fuzzy", max_length=50)  # fuzzy, anomaly, watchdog, threshold
    fuzzy_level: float = Field(default=0.0)
    resolved_by: Optional[str] = Field(default=None, max_length=50)
    resolved_at: Optional[datetime] = Field(default=None)
    read_at: Optional[datetime] = Field(default=None)


class MaintenanceRecord(SQLModel, table=True):
    """Registro de mantenimiento realizado a un grupo electrógeno."""
    __tablename__ = "maintenance_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    node_id: str = Field(index=True, max_length=20)
    fecha: datetime = Field(default_factory=datetime.utcnow)
    tecnico: str = Field(max_length=100)
    tipo: str = Field(max_length=50)  # cambio_aceite, cambio_filtro, inspeccion, reparacion
    descripcion: str = Field(default="", max_length=1000)
    repuestos: str = Field(default="", max_length=500)
    horas_equipo: float = Field(default=0.0)
    proximo_servicio: Optional[datetime] = Field(default=None)
    costo: float = Field(default=0.0)
    observaciones: str = Field(default="", max_length=500)


class NodeConfig(SQLModel, table=True):
    """Configuración y geolocalización de cada nodo."""
    __tablename__ = "node_configs"

    id: Optional[int] = Field(default=None, primary_key=True)
    node_id: str = Field(unique=True, index=True, max_length=20)
    nombre: str = Field(max_length=100)
    localidad: str = Field(max_length=100)
    zona: str = Field(max_length=50)
    lat: float = Field(default=-26.18)
    lon: float = Field(default=-58.18)
    direccion: str = Field(default="", max_length=200)
    capacidad_kw: float = Field(default=0.0)
    modelo_equipo: str = Field(default="", max_length=100)
    fecha_instalacion: Optional[datetime] = Field(default=None)
    activo: bool = Field(default=True)


class NodeWatchdogEvent(SQLModel, table=True):
    """Registro de eventos de conectividad de nodos."""
    __tablename__ = "watchdog_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    node_id: str = Field(index=True, max_length=20)
    event_type: str = Field(max_length=20)  # "offline", "recovery"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    downtime_seconds: Optional[float] = Field(default=None)
    details: str = Field(default="", max_length=500)


# ── Engine y sesión ──────────────────────────────────────────

_engine = None


def _get_engine():
    """Obtiene (o crea) el engine singleton de SQLModel."""
    global _engine
    if _engine is None:
        s = get_settings()
        db_url = f"sqlite:///{s.app_db_path}"
        _engine = create_engine(db_url, echo=False)
    return _engine


def init_db():
    """Crea todas las tablas si no existen."""
    engine = _get_engine()
    SQLModel.metadata.create_all(engine)
    logger.info("✅ Base de datos de aplicación inicializada: %s", get_settings().app_db_path)


def get_session() -> Generator[Session, None, None]:
    """Genera una sesión de base de datos para usar con FastAPI Depends."""
    engine = _get_engine()
    with Session(engine) as session:
        yield session
