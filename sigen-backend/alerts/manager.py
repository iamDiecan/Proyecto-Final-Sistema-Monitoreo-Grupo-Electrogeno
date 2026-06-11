# sigen-backend/alerts/manager.py
"""
Gestor de Alertas. Encargado de persistir, consultar y resolver alertas.
"""
from typing import List, Optional
from datetime import datetime

from sqlmodel import Session, select
from models.database import Alert, AlertStatus
import asyncio

try:
    from telegram_bot import send_telegram_alert
except ImportError:
    send_telegram_alert = None

# Umbrales estáticos (idealmente vienen de DB/Config, pero los hardcodeamos según reqs)
THRESHOLDS = {
    "voltaje": {"min": 210, "max": 230, "crit_min": 190, "crit_max": 250},
    "corriente": {"min": 0, "max": 500, "crit_max": 800},
    "frecuencia": {"min": 59, "max": 61, "crit_min": 55, "crit_max": 65},
    "temp_motor": {"min": 70, "max": 95, "crit_max": 110},
    "presion_aceite": {"min": 3, "max": 7, "crit_min": 1, "crit_max": 9},
    "combustible_pct": {"min": 20, "crit_min": 10}
}

def evaluate_telemetry(node_id: str, reading: dict) -> List[dict]:
    """Evalúa la telemetría cruda y devuelve una lista de alertas si hay desviaciones."""
    alerts = []
    
    # helper para chequear un param
    def check_param(param_key: str, param_name: str, unit: str):
        val = reading.get(param_key)
        if val is None:
            return
            
        th = THRESHOLDS.get(param_key, {})
        val = float(val)
        
        # Check Crítico
        if ("crit_max" in th and val >= th["crit_max"]) or ("crit_min" in th and val <= th["crit_min"]):
            alerts.append({
                "level": "emergencia",
                "title": f"🔴 CRÍTICO: {param_name} Anormal",
                "description": f"Valor: {val:.1f} {unit} (Límite: {th.get('crit_min', 'N/A')} - {th.get('crit_max', 'N/A')})",
                "fuzzy_level": 100.0
            })
        # Check Advertencia
        elif ("max" in th and val > th["max"]) or ("min" in th and val < th["min"]):
            alerts.append({
                "level": "alerta",
                "title": f"🟡 ADVERTENCIA: {param_name} Fuera de Rango",
                "description": f"Valor: {val:.1f} {unit} (Normal: {th.get('min', 'N/A')} - {th.get('max', 'N/A')})",
                "fuzzy_level": 60.0
            })

    check_param("voltaje", "Tensión", "V")
    check_param("corriente", "Corriente", "A")
    check_param("frecuencia", "Frecuencia", "Hz")
    check_param("temp_motor", "Temperatura Motor", "°C")
    check_param("presion_aceite", "Presión de Aceite", "bar")
    check_param("combustible_pct", "Nivel de Combustible", "%")
    
    return alerts

def create_alerts(session: Session, node_id: str, alerts_data: List[dict]) -> List[Alert]:
    """Crea nuevas alertas en la base de datos si no existen alertas activas similares."""
    created_alerts = []
    
    for alert_data in alerts_data:
        # Prevención de spam: Verificar si ya hay una alerta ACTIVA del mismo nivel y título para este nodo
        statement = select(Alert).where(
            Alert.node_id == node_id,
            Alert.status == AlertStatus.ACTIVE.value,
            Alert.title == alert_data["title"]
        )
        existing = session.exec(statement).first()
        
        if not existing:
            new_alert = Alert(
                node_id=node_id,
                level=alert_data["level"],
                title=alert_data["title"],
                description=alert_data["description"],
                fuzzy_level=alert_data["fuzzy_level"],
                source="anomaly_engine"
            )
            session.add(new_alert)
            created_alerts.append(new_alert)
            
    if created_alerts:
        session.commit()
        for a in created_alerts:
            session.refresh(a)
            
            # Enviar notificación a Telegram
            if send_telegram_alert:
                msg = f"*{a.title}*\nNodo: {a.node_id}\nDetalle: {a.description}"
                try:
                    # Al estar en un contexto asíncrono o no, lanzamos la corrutina
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        loop.create_task(send_telegram_alert(msg))
                    else:
                        asyncio.run(send_telegram_alert(msg))
                except Exception as e:
                    print(f"Error despachando alerta Telegram: {e}")
            
    return created_alerts

def get_alerts(
    session: Session, 
    node_id: Optional[str] = None, 
    status: Optional[str] = None,
    limit: int = 50
) -> List[Alert]:
    """Obtiene alertas filtradas."""
    statement = select(Alert)
    
    if node_id:
        statement = statement.where(Alert.node_id == node_id)
    if status:
        statement = statement.where(Alert.status == status)
        
    statement = statement.order_by(Alert.timestamp.desc()).limit(limit)
    return session.exec(statement).all()

def resolve_alert(session: Session, alert_id: int, resolved_by: str) -> Optional[Alert]:
    """Marca una alerta como resuelta."""
    alert = session.get(Alert, alert_id)
    if alert:
        alert.status = AlertStatus.RESOLVED.value
        alert.resolved_by = resolved_by
        alert.resolved_at = datetime.utcnow()
        session.add(alert)
        session.commit()
        session.refresh(alert)
    return alert

def mark_alert_read(session: Session, alert_id: int) -> Optional[Alert]:
    """Marca una alerta como leída."""
    alert = session.get(Alert, alert_id)
    if alert and alert.status == AlertStatus.ACTIVE.value:
        alert.status = AlertStatus.READ.value
        alert.read_at = datetime.utcnow()
        session.add(alert)
        session.commit()
        session.refresh(alert)
    return alert
