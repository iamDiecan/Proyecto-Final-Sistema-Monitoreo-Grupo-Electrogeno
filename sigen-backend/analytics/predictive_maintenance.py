# sigen-backend/analytics/predictive_maintenance.py
"""
Módulo de Mantenimiento Predictivo para SIGEGEN v3.0

Calcula predicciones de próximos servicios basándose en:
  - Horas acumuladas del motor
  - Último mantenimiento registrado
  - Intervalos configurables
  - Tendencia de uso (promedio de horas/día)

Servicios predictivos:
  - Cambio de aceite:  cada 250h (configurable)
  - Cambio de filtros: cada 500h (configurable)
  - Inspección general: cada 1000h (configurable)
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlmodel import Session, select

from config import get_settings
from models.database import MaintenanceRecord

logger = logging.getLogger("sigegen.predictive_maintenance")


# ── Tipos de servicio ────────────────────────────────────────

SERVICE_TYPES = {
    "cambio_aceite": {
        "label": "Cambio de Aceite",
        "icon": "droplet",
        "color": "#F59E0B",
        "priority": 1,
    },
    "cambio_filtro": {
        "label": "Cambio de Filtros",
        "icon": "filter",
        "color": "#3B82F6",
        "priority": 2,
    },
    "inspeccion": {
        "label": "Inspección General",
        "icon": "search",
        "color": "#8B5CF6",
        "priority": 3,
    },
}


def _get_interval_hours(service_type: str) -> int:
    """Obtiene el intervalo de horas configurado para un tipo de servicio."""
    s = get_settings()
    intervals = {
        "cambio_aceite": s.maintenance_oil_change_hours,
        "cambio_filtro": s.maintenance_filter_change_hours,
        "inspeccion": s.maintenance_inspection_hours,
    }
    return intervals.get(service_type, 500)


def _get_last_maintenance(session: Session, node_id: str, tipo: str) -> Optional[MaintenanceRecord]:
    """Obtiene el último registro de mantenimiento de un tipo para un nodo."""
    statement = (
        select(MaintenanceRecord)
        .where(MaintenanceRecord.node_id == node_id)
        .where(MaintenanceRecord.tipo == tipo)
        .order_by(MaintenanceRecord.fecha.desc())
    )
    return session.exec(statement).first()


def calculate_predictions(
    session: Session,
    node_id: str,
    horas_motor: float,
    avg_hours_per_day: float = 8.0,
) -> List[Dict[str, Any]]:
    """
    Calcula predicciones de mantenimiento para un nodo.

    Args:
        session: Sesión de SQLModel.
        node_id: ID del nodo.
        horas_motor: Horas acumuladas actuales del motor.
        avg_hours_per_day: Promedio de horas de funcionamiento por día.

    Returns:
        Lista de predicciones con: tipo, label, horas_restantes, fecha_estimada,
        porcentaje_vida, estado (ok/warning/overdue).
    """
    predictions = []

    for service_type, info in SERVICE_TYPES.items():
        interval = _get_interval_hours(service_type)
        last_record = _get_last_maintenance(session, node_id, service_type)

        if last_record:
            horas_desde_ultimo = horas_motor - last_record.horas_equipo
            fecha_ultimo = last_record.fecha
        else:
            # Sin registro previo: asumir mantenimiento desde la hora 0
            horas_desde_ultimo = horas_motor
            fecha_ultimo = None

        horas_restantes = max(0, interval - horas_desde_ultimo)
        porcentaje_vida = min(100.0, (horas_desde_ultimo / interval) * 100.0)

        # Estimar fecha del próximo servicio
        if avg_hours_per_day > 0 and horas_restantes > 0:
            dias_restantes = horas_restantes / avg_hours_per_day
            fecha_estimada = datetime.utcnow() + timedelta(days=dias_restantes)
        else:
            dias_restantes = 0
            fecha_estimada = datetime.utcnow()

        # Estado
        if horas_restantes <= 0:
            estado = "overdue"
            urgencia = "URGENTE"
            estado_color = "#EF4444"
        elif porcentaje_vida >= 80:
            estado = "warning"
            urgencia = "PRÓXIMO"
            estado_color = "#F59E0B"
        else:
            estado = "ok"
            urgencia = "OK"
            estado_color = "#10B981"

        predictions.append({
            "tipo": service_type,
            "label": info["label"],
            "icon": info["icon"],
            "color": info["color"],
            "interval_hours": interval,
            "horas_desde_ultimo": round(horas_desde_ultimo, 1),
            "horas_restantes": round(horas_restantes, 1),
            "porcentaje_vida": round(porcentaje_vida, 1),
            "dias_restantes": round(dias_restantes, 0),
            "fecha_estimada": fecha_estimada.strftime("%Y-%m-%d"),
            "fecha_ultimo": fecha_ultimo.strftime("%Y-%m-%d") if fecha_ultimo else "Sin registro",
            "estado": estado,
            "urgencia": urgencia,
            "estado_color": estado_color,
            "priority": info["priority"],
        })

    # Ordenar por urgencia (overdue primero)
    priority_order = {"overdue": 0, "warning": 1, "ok": 2}
    predictions.sort(key=lambda p: (priority_order.get(p["estado"], 2), p["priority"]))

    return predictions


def get_maintenance_summary(
    session: Session,
    node_ids: List[str],
    horas_por_nodo: Dict[str, float],
) -> Dict[str, Any]:
    """
    Resumen de mantenimiento para múltiples nodos.

    Returns:
        Dict con: overdue_count, warning_count, ok_count, critical_nodes.
    """
    overdue = 0
    warning = 0
    ok = 0
    critical_nodes = []

    for node_id in node_ids:
        horas = horas_por_nodo.get(node_id, 0)
        preds = calculate_predictions(session, node_id, horas)
        for p in preds:
            if p["estado"] == "overdue":
                overdue += 1
                if node_id not in critical_nodes:
                    critical_nodes.append(node_id)
            elif p["estado"] == "warning":
                warning += 1
            else:
                ok += 1

    return {
        "overdue_count": overdue,
        "warning_count": warning,
        "ok_count": ok,
        "critical_nodes": critical_nodes,
        "total_services_tracked": len(node_ids) * len(SERVICE_TYPES),
    }
