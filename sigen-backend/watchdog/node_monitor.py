# sigen-backend/watchdog/node_monitor.py
"""
Monitor de Nodos (Watchdog).
Verifica periódicamente el timestamp del último mensaje recibido de cada nodo.
Si un nodo no reporta en más del tiempo configurado, se marca como offline
y se genera una alerta.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from sqlmodel import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import get_settings
from models.database import NodeWatchdogEvent, AlertLevel, _get_engine
from alerts.manager import create_alerts, evaluate_telemetry
import influx_client

logger = logging.getLogger("sigegen.watchdog")

class NodeMonitor:
    def __init__(self):
        self.last_seen: Dict[str, datetime] = {}
        self.node_status: Dict[str, str] = {}  # "online" o "offline"
        self.scheduler = AsyncIOScheduler()
        self._setup()
        
    def _setup(self):
        s = get_settings()
        self.timeout_minutes = s.watchdog_timeout_minutes
        interval = s.watchdog_check_interval_seconds
        
        self.scheduler.add_job(
            self.check_nodes,
            'interval',
            seconds=interval,
            id='watchdog_check'
        )
        self.scheduler.add_job(
            self.check_telemetry,
            'interval',
            seconds=interval,
            id='telemetry_check'
        )
        
    def start(self):
        self.scheduler.start()
        logger.info("Watchdog iniciado. Timeout: %d min", self.timeout_minutes)
        
    def stop(self):
        self.scheduler.shutdown()
        
    def update_node(self, node_id: str):
        """Llamado cada vez que se recibe un mensaje de un nodo."""
        now = datetime.utcnow()
        was_offline = self.node_status.get(node_id) == "offline"
        
        self.last_seen[node_id] = now
        self.node_status[node_id] = "online"
        
        if was_offline:
            # Registrar recuperación
            self._handle_recovery(node_id, now)
            
    async def check_nodes(self):
        """Verifica todos los nodos conocidos."""
        now = datetime.utcnow()
        timeout_delta = timedelta(minutes=self.timeout_minutes)
        
        for node_id, last_time in self.last_seen.items():
            if self.node_status.get(node_id) == "online":
                if now - last_time > timeout_delta:
                    self._handle_offline(node_id, now, last_time)

    async def check_telemetry(self):
        """Revisa la última telemetría de InfluxDB para disparar alertas proactivas."""
        readings = influx_client.get_all_last_readings()
        if not readings:
            return
            
        engine = _get_engine()
        with Session(engine) as session:
            for r in readings:
                node_id = r.get("nodo_id")
                if not node_id:
                    continue
                # Actualizar watchdog last_seen
                self.update_node(node_id)
                
                # Evaluar parámetros
                alert_data = evaluate_telemetry(node_id, r)
                if alert_data:
                    create_alerts(session, node_id, alert_data)

    def _handle_offline(self, node_id: str, now: datetime, last_time: datetime):
        """Maneja la transición de un nodo a offline."""
        logger.warning(f"Nodo {node_id} está OFFLINE. Última vez visto: {last_time}")
        self.node_status[node_id] = "offline"
        
        engine = _get_engine()
        with Session(engine) as session:
            # 1. Registrar evento
            event = NodeWatchdogEvent(
                node_id=node_id,
                event_type="offline",
                timestamp=now,
                details=f"Pérdida de conectividad. Último reporte: {last_time.isoformat()}Z"
            )
            session.add(event)
            
            # 2. Generar alerta
            alert_data = [{
                "level": AlertLevel.CRITICAL.value,
                "title": "Pérdida de Conectividad (Nodo Offline)",
                "description": f"El nodo no ha reportado datos en más de {self.timeout_minutes} minutos.",
                "fuzzy_level": 100.0  # Máximo nivel para offline
            }]
            create_alerts(session, node_id, alert_data)
            
            session.commit()

    def _handle_recovery(self, node_id: str, now: datetime):
        """Maneja la recuperación de conectividad de un nodo."""
        logger.info(f"Nodo {node_id} se ha RECUPERADO.")
        
        engine = _get_engine()
        with Session(engine) as session:
            # Obtener el último evento offline para calcular downtime
            # Por simplicidad, se asume que el downtime es aprox la diferencia
            
            event = NodeWatchdogEvent(
                node_id=node_id,
                event_type="recovery",
                timestamp=now,
                details="Conectividad restablecida."
            )
            session.add(event)
            
            # Generar alerta INFO de recuperación
            alert_data = [{
                "level": AlertLevel.INFO.value,
                "title": "Conectividad Restablecida",
                "description": "El nodo ha vuelto a reportar datos.",
                "fuzzy_level": 0.0
            }]
            create_alerts(session, node_id, alert_data)
            
            session.commit()
            
    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual de todos los nodos."""
        return {
            "status": self.node_status,
            "last_seen": {k: v.isoformat() + "Z" for k, v in self.last_seen.items()}
        }

# Singleton
_monitor_instance = None

def get_node_monitor() -> NodeMonitor:
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = NodeMonitor()
    return _monitor_instance
