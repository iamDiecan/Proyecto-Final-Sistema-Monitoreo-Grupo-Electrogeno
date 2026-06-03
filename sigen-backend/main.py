# sigen-backend/main.py
"""
API backend de SIGEGEN v2.0
Fuente de datos: InfluxDB (principal) con fallback automático a SQLite.
"""
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import sqlite3
import os
import json
from typing import List, Dict, Any, Optional

from config import get_settings
import influx_client

# ── Sistema difuso ──────────────────────────────────────────
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from sigegen_fuzzy_alerts import FuzzyAlertSystem
    fuzzy_system = FuzzyAlertSystem()
except Exception as e:
    print(f"Error cargando sistema difuso: {e}")
    fuzzy_system = None

# ── Logging ─────────────────────────────────────────────────
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("sigegen.api")

# ── Estado de conexión ──────────────────────────────────────
_influx_available = False


def is_influx_available() -> bool:
    """Indica si InfluxDB respondió al último healthcheck."""
    return _influx_available


# ── Lifespan (startup / shutdown) ───────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _influx_available
    # Startup: verificar InfluxDB
    if settings.influxdb_token:
        _influx_available = influx_client.check_connection()
        if _influx_available:
            logger.info("✅ InfluxDB conectado en %s", settings.influxdb_url)
        else:
            logger.warning("⚠️ InfluxDB NO disponible – usando SQLite como fallback")
    else:
        logger.info("ℹ️ Token de InfluxDB vacío – usando SQLite directamente")

    yield

    # Shutdown: cerrar cliente InfluxDB
    influx_client.close_client()
    logger.info("🔌 Cliente InfluxDB cerrado")


app = FastAPI(title="SIGEGEN API", version="2.0.0", lifespan=lifespan)

# Permitir CORS para desarrollo local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción restringir a dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── SQLite helpers (fallback) ───────────────────────────────
DB_PATH = settings.sqlite_db_path


def get_db_connection():
    """Crea una conexión a la base de datos SQLite y retorna un cursor de diccionario."""
    if not os.path.exists(DB_PATH):
        raise HTTPException(
            status_code=500,
            detail=f"Base de datos no encontrada en {DB_PATH}. Corra el simulador primero para generarla."
        )
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def parse_row(row) -> Dict[str, Any]:
    """Convierte una fila de SQLite o dict de InfluxDB a un diccionario compatible con JSON."""
    d = dict(row) if not isinstance(row, dict) else dict(row)

    # Parsear alarmas si viene como string JSON
    if "alarmas" in d and d["alarmas"]:
        try:
            d["alarmas"] = json.loads(d["alarmas"])
        except Exception:
            d["alarmas"] = []

    # Evaluar con lógica difusa para obtener las contribuciones dinámicas en tiempo real
    contribuciones = {}
    if fuzzy_system:
        try:
            nivel, categoria, contrib = fuzzy_system.evaluate(d)
            d["alerta_difusa_nivel"] = nivel
            d["alerta_difusa_categoria"] = categoria
            contribuciones = contrib
        except Exception as ex:
            logger.debug("Error evaluando fila difusa: %s", ex)
    d["alerta_difusa_contribuciones"] = contribuciones

    # Calcular colores de contribución para el frontend
    contrib_colores = {}
    for k, val in contribuciones.items():
        v_f = float(val) if val is not None else 0.0
        if v_f > 75.0:
            contrib_colores[k] = "#EF4444"
        elif v_f > 40.0:
            contrib_colores[k] = "#F97316"
        else:
            contrib_colores[k] = "#10B981"
    d["alerta_difusa_contribuciones_colores"] = contrib_colores

    # Calcular color del combustible
    comb = d.get("combustible_pct", 50.0)
    comb = float(comb) if comb is not None else 50.0
    if comb > 50.0:
        d["fuel_color"] = "#10B981"
    elif comb > 20.0:
        d["fuel_color"] = "#F59E0B"
    else:
        d["fuel_color"] = "#EF4444"

    # Calcular color del estado de alerta
    alerta_lvl = d.get("alerta_difusa_nivel", 0.0)
    alerta_lvl = float(alerta_lvl) if alerta_lvl is not None else 0.0
    if alerta_lvl > 75.0:
        d["alert_color"] = "#EF4444"
    elif alerta_lvl > 35.0:
        d["alert_color"] = "#F97316"
    else:
        d["alert_color"] = "#10B981"

    return d


def _add_frontend_fields(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Agrega campos amigables para el frontend (id, nombre)."""
    nodo_id = parsed.get("nodo_id", "nodo_00")
    parsed["id"] = nodo_id
    parts = nodo_id.split("_")
    parsed["nombre"] = f"Generador {parts[1]}" if len(parts) > 1 else f"Generador {nodo_id}"
    return parsed


# ── Funciones de obtención de datos (dual source) ──────────
def _fetch_generadores_influx() -> Optional[List[Dict[str, Any]]]:
    """Intenta obtener generadores desde InfluxDB."""
    rows = influx_client.get_all_last_readings()
    if rows is None:
        return None
    return [_add_frontend_fields(parse_row(r)) for r in rows]


def _fetch_generadores_sqlite() -> List[Dict[str, Any]]:
    """Obtiene generadores desde SQLite (fallback)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT l1.* FROM lecturas l1
        INNER JOIN (
            SELECT nodo_id, MAX(timestamp) as max_ts
            FROM lecturas
            GROUP BY nodo_id
        ) l2 ON l1.nodo_id = l2.nodo_id AND l1.timestamp = l2.max_ts
        ORDER BY l1.nodo_id
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return [_add_frontend_fields(parse_row(r)) for r in rows]


def _fetch_ultima_lectura_influx(generador_id: str) -> Optional[Dict[str, Any]]:
    """Última lectura de un nodo desde InfluxDB."""
    row = influx_client.get_last_reading(generador_id)
    if row is None:
        return None
    return _add_frontend_fields(parse_row(row))


def _fetch_ultima_lectura_sqlite(generador_id: str) -> Optional[Dict[str, Any]]:
    """Última lectura de un nodo desde SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM lecturas WHERE nodo_id = ? ORDER BY timestamp DESC LIMIT 1",
        (generador_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return _add_frontend_fields(parse_row(row))


def _fetch_historial_influx(generador_id: str, limite: int) -> Optional[List[Dict[str, Any]]]:
    """Historial de un nodo desde InfluxDB."""
    rows = influx_client.get_history(generador_id, limite)
    if rows is None:
        return None
    return [_add_frontend_fields(parse_row(r)) for r in rows]


def _fetch_historial_sqlite(generador_id: str, limite: int) -> List[Dict[str, Any]]:
    """Historial de un nodo desde SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT * FROM (
            SELECT * FROM lecturas 
            WHERE nodo_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ) ORDER BY timestamp ASC
    """
    cursor.execute(query, (generador_id, limite))
    rows = cursor.fetchall()
    conn.close()
    return [_add_frontend_fields(parse_row(r)) for r in rows]


def _fetch_alertas_influx(limite: int) -> Optional[List[Dict[str, Any]]]:
    """Alertas desde InfluxDB."""
    rows = influx_client.get_alerts(limite)
    if rows is None:
        return None
    return [_add_frontend_fields(parse_row(r)) for r in rows]


def _fetch_alertas_sqlite(limite: int) -> List[Dict[str, Any]]:
    """Alertas desde SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT * FROM lecturas 
        WHERE alerta_difusa_nivel >= 35 OR estado != 'normal'
        ORDER BY timestamp DESC 
        LIMIT ?
    """
    cursor.execute(query, (limite,))
    rows = cursor.fetchall()
    conn.close()
    return [_add_frontend_fields(parse_row(r)) for r in rows]


def _fetch_resumen_influx() -> Optional[Dict[str, Any]]:
    """Resumen global desde InfluxDB."""
    rows = influx_client.get_summary_data()
    if rows is None:
        return None
    return _compute_resumen(rows)


def _fetch_resumen_sqlite() -> Dict[str, Any]:
    """Resumen global desde SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT l1.estado, l1.alerta_difusa_nivel, l1.combustible_pct, l1.encendido 
        FROM lecturas l1
        INNER JOIN (
            SELECT nodo_id, MAX(timestamp) as max_ts
            FROM lecturas
            GROUP BY nodo_id
        ) l2 ON l1.nodo_id = l2.nodo_id AND l1.timestamp = l2.max_ts
    """
    cursor.execute(query)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return _compute_resumen(rows)


def _compute_resumen(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calcula métricas de resumen a partir de una lista de lecturas."""
    total = len(rows)
    if total == 0:
        return {
            "total": 0, "encendidos": 0, "apagados": 0,
            "normal": 0, "alerta": 0, "falla": 0,
            "alerta_promedio": 0.0, "combustible_promedio": 0.0,
        }

    encendidos = sum(1 for r in rows if r.get("encendido"))
    normal = sum(1 for r in rows if r.get("estado") == "normal")
    alerta = sum(1 for r in rows if r.get("estado") == "alerta")
    falla = sum(1 for r in rows if r.get("estado") == "falla")
    alerta_promedio = sum(float(r.get("alerta_difusa_nivel", 0) or 0) for r in rows) / total
    combustible_promedio = sum(float(r.get("combustible_pct", 0) or 0) for r in rows) / total

    return {
        "total": total,
        "encendidos": encendidos,
        "apagados": total - encendidos,
        "normal": normal,
        "alerta": alerta,
        "falla": falla,
        "alerta_promedio": round(alerta_promedio, 1),
        "combustible_promedio": round(combustible_promedio, 1),
    }


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS
# ══════════════════════════════════════════════════════════════

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "SIGEGEN API funcionando correctamente",
        "database_path": DB_PATH,
        "exists": os.path.exists(DB_PATH),
        "influxdb_available": is_influx_available(),
    }


@app.get("/health")
def health():
    """Healthcheck: verifica la conexión a InfluxDB y la existencia de SQLite."""
    global _influx_available
    _influx_available = influx_client.check_connection()

    sqlite_ok = os.path.exists(DB_PATH)
    status = "ok" if (_influx_available or sqlite_ok) else "unhealthy"

    return {
        "status": status,
        "influxdb": "connected" if _influx_available else "disconnected",
        "sqlite": "available" if sqlite_ok else "unavailable",
        "mode": "influxdb" if _influx_available else ("sqlite_fallback" if sqlite_ok else "no_datasource"),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/api/generadores")
def get_generadores():
    """Retorna la lista de todos los generadores con su último estado y telemetría."""
    try:
        # Intentar InfluxDB primero
        if is_influx_available():
            result = _fetch_generadores_influx()
            if result is not None:
                return result
            logger.warning("InfluxDB falló – cayendo a SQLite")

        # Fallback a SQLite
        return _fetch_generadores_sqlite()
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error en /api/generadores: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/telemetria/{generador_id}/ultimo")
def get_ultima_lectura(generador_id: str):
    """Retorna la última lectura de telemetría de un generador específico."""
    try:
        if is_influx_available():
            result = _fetch_ultima_lectura_influx(generador_id)
            if result is not None:
                return result

        result = _fetch_ultima_lectura_sqlite(generador_id)
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontraron lecturas para el generador '{generador_id}'",
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error en /api/telemetria/%s/ultimo: %s", generador_id, e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/telemetria/{generador_id}/historial")
def get_historial_lecturas(generador_id: str, limite: int = 20):
    """Retorna las últimas N lecturas de un generador, ordenadas cronológicamente."""
    try:
        if is_influx_available():
            result = _fetch_historial_influx(generador_id, limite)
            if result is not None:
                return result

        return _fetch_historial_sqlite(generador_id, limite)
    except Exception as e:
        logger.error("Error en /api/telemetria/%s/historial: %s", generador_id, e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alertas")
def get_alertas_recientes(limite: int = 50):
    """Retorna las lecturas con nivel de alerta difuso alto (>= 35) o alarmas activas."""
    try:
        if is_influx_available():
            result = _fetch_alertas_influx(limite)
            if result is not None:
                return result

        return _fetch_alertas_sqlite(limite)
    except Exception as e:
        logger.error("Error en /api/alertas: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/resumen")
def get_resumen_global():
    """Retorna un resumen del estado de todos los generadores para el dashboard."""
    try:
        if is_influx_available():
            result = _fetch_resumen_influx()
            if result is not None:
                return result

        return _fetch_resumen_sqlite()
    except Exception as e:
        logger.error("Error en /api/resumen: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
