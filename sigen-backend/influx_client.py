# sigen-backend/influx_client.py
"""
Cliente singleton para InfluxDB con cache en memoria, timeouts y healthcheck.

Funciones principales:
  - check_connection()          → bool
  - get_all_last_readings()     → list[dict] | None
  - get_last_reading(nodo_id)   → dict | None
  - get_history(nodo_id, limit) → list[dict] | None
  - get_alerts(limit)           → list[dict] | None
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from cachetools import TTLCache
from influxdb_client import InfluxDBClient
from influxdb_client.client.exceptions import InfluxDBError

from config import get_settings

logger = logging.getLogger(__name__)

# ── Singleton del cliente ───────────────────────────────────
_client: InfluxDBClient | None = None
_cache: TTLCache | None = None


def _get_client() -> InfluxDBClient:
    """Obtiene (o crea) el cliente singleton de InfluxDB."""
    global _client
    if _client is None:
        s = get_settings()
        _client = InfluxDBClient(
            url=s.influxdb_url,
            token=s.influxdb_token,
            org=s.influxdb_org,
            timeout=s.influxdb_timeout_ms,
        )
    return _client


def _get_cache() -> TTLCache:
    """Obtiene (o crea) el cache singleton con TTL configurable."""
    global _cache
    if _cache is None:
        s = get_settings()
        _cache = TTLCache(maxsize=s.cache_max_size, ttl=s.cache_ttl_seconds)
    return _cache


def close_client() -> None:
    """Cierra el cliente de InfluxDB (llamar al apagar la app)."""
    global _client
    if _client is not None:
        _client.close()
        _client = None


# ── Healthcheck ─────────────────────────────────────────────
def check_connection() -> bool:
    """Verifica que InfluxDB esté accesible. Retorna True si responde."""
    try:
        health = _get_client().health()
        return health.status == "pass"
    except Exception as exc:
        logger.warning("InfluxDB healthcheck falló: %s", exc)
        return False


# ── Ejecución de queries Flux ───────────────────────────────
def _query_flux(flux: str, cache_key: str | None = None) -> Optional[List[Dict[str, Any]]]:
    """
    Ejecuta una consulta Flux y retorna una lista de diccionarios.
    Usa cache si se proporciona `cache_key`.
    Retorna None si InfluxDB no está disponible.
    """
    # Verificar cache
    if cache_key is not None:
        cache = _get_cache()
        cached = cache.get(cache_key)
        if cached is not None:
            logger.debug("Cache hit: %s", cache_key)
            return cached

    try:
        client = _get_client()
        s = get_settings()
        query_api = client.query_api()
        tables = query_api.query(flux, org=s.influxdb_org)

        results: List[Dict[str, Any]] = []
        for table in tables:
            for record in table.records:
                row = dict(record.values)
                # Renombrar _time → timestamp para compatibilidad con el frontend
                if "_time" in row:
                    row["timestamp"] = str(row.pop("_time"))
                results.append(row)

        # Guardar en cache
        if cache_key is not None and results is not None:
            _get_cache()[cache_key] = results

        return results

    except InfluxDBError as exc:
        logger.error("Error en query Flux: %s", exc)
        return None
    except Exception as exc:
        logger.error("Error inesperado consultando InfluxDB: %s", exc)
        return None


# ── Funciones de consulta específicas ───────────────────────
def get_all_last_readings() -> Optional[List[Dict[str, Any]]]:
    """
    Obtiene la última lectura de cada nodo (generador).
    Equivale a:
      SELECT l1.* FROM lecturas l1
      INNER JOIN (SELECT nodo_id, MAX(timestamp) ...) ...
    """
    s = get_settings()
    flux = f'''
        from(bucket: "{s.influxdb_bucket}")
          |> range(start: -24h)
          |> filter(fn: (r) => r["_measurement"] == "lecturas")
          |> last()
          |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    return _query_flux(flux, cache_key="all_last_readings")


def get_last_reading(nodo_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene la última lectura de un nodo específico."""
    s = get_settings()
    flux = f'''
        from(bucket: "{s.influxdb_bucket}")
          |> range(start: -24h)
          |> filter(fn: (r) => r["_measurement"] == "lecturas")
          |> filter(fn: (r) => r["nodo_id"] == "{nodo_id}")
          |> last()
          |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    results = _query_flux(flux, cache_key=f"last_{nodo_id}")
    if results and len(results) > 0:
        return results[0]
    return None


def get_history(nodo_id: str, limit: int = 20) -> Optional[List[Dict[str, Any]]]:
    """Obtiene las últimas N lecturas de un nodo, ordenadas cronológicamente."""
    s = get_settings()
    flux = f'''
        from(bucket: "{s.influxdb_bucket}")
          |> range(start: -7d)
          |> filter(fn: (r) => r["_measurement"] == "lecturas")
          |> filter(fn: (r) => r["nodo_id"] == "{nodo_id}")
          |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
          |> sort(columns: ["_time"], desc: true)
          |> limit(n: {limit})
          |> sort(columns: ["_time"], desc: false)
    '''
    return _query_flux(flux, cache_key=f"hist_{nodo_id}_{limit}")


def get_alerts(limit: int = 50) -> Optional[List[Dict[str, Any]]]:
    """Obtiene lecturas con alerta difusa >= 35 o estado != 'normal'."""
    s = get_settings()
    flux = f'''
        from(bucket: "{s.influxdb_bucket}")
          |> range(start: -24h)
          |> filter(fn: (r) => r["_measurement"] == "lecturas")
          |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
          |> filter(fn: (r) =>
              (r["alerta_difusa_nivel"] >= 35.0) or
              (r["estado"] != "normal")
          )
          |> sort(columns: ["_time"], desc: true)
          |> limit(n: {limit})
    '''
    return _query_flux(flux, cache_key=f"alerts_{limit}")


def get_summary_data() -> Optional[List[Dict[str, Any]]]:
    """Obtiene campos de resumen de la última lectura de cada nodo."""
    s = get_settings()
    flux = f'''
        from(bucket: "{s.influxdb_bucket}")
          |> range(start: -24h)
          |> filter(fn: (r) => r["_measurement"] == "lecturas")
          |> last()
          |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    return _query_flux(flux, cache_key="summary_data")
