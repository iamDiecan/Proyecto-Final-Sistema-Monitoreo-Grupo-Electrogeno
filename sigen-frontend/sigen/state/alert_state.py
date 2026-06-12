# sigen-frontend/sigen/state/alert_state.py
import reflex as rx
import httpx
from typing import List, Dict, Any
from sigen.state.auth_state import AuthState

class AlertState(rx.State):
    """Estado global para el Centro de Alertas."""
    alerts: List[Dict[str, Any]] = []
    
    async def fetch_alerts(self):
        """Obtiene todas las alertas activas desde la API."""
        auth_token = await self.get_state(AuthState)
        token = auth_token.token
        
        if not token:
            self.load_mock_alerts()
            return
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "http://localhost:8002/api/alerts/?limit=100",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code == 200:
                    data = response.json()
                    
                    # Normalizar para el componente de tabla
                    normalized = []
                    for d in data:
                        lvl = d.get("level", "INFO")
                        c = "red" if lvl == "CRITICAL" else ("orange" if lvl == "WARNING" else "blue")
                        normalized.append({
                            "id": d.get("id"),
                            "title": d.get("title", "Alerta"),
                            "level": lvl,
                            "node": d.get("node_id", "Unknown"),
                            "status": d.get("status", "activa"),
                            "color": c
                        })
                    self.alerts = normalized
                else:
                    self.load_mock_alerts()
        except Exception as e:
            print(f"Error fetching alerts: {e}")
            self.load_mock_alerts()

    def load_mock_alerts(self):
        self.alerts = [
            {
                "id": 1,
                "title": "Temperatura de motor excesiva (>95°C)",
                "level": "CRITICAL",
                "node": "nodo_02",
                "status": "activa",
                "color": "red"
            },
            {
                "id": 2,
                "title": "Nivel de combustible bajo (<15%)",
                "level": "WARNING",
                "node": "nodo_01",
                "status": "activa",
                "color": "orange"
            },
            {
                "id": 3,
                "title": "Pérdida de telemetría de red",
                "level": "CRITICAL",
                "node": "nodo_03",
                "status": "activa",
                "color": "red"
            }
        ]
