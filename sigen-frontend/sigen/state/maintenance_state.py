# sigen-frontend/sigen/state/maintenance_state.py
import reflex as rx
import httpx
from typing import List, Dict, Any
from sigen.state.auth_state import AuthState

class MaintenanceState(rx.State):
    """Estado global para Mantenimiento."""
    records: List[Dict[str, Any]] = []
    
    # Form state for mock
    form_nodo: str = ""
    form_fecha: str = ""
    form_tipo: str = "Preventivo"
    form_tecnico: str = ""
    form_horas: str = ""
    form_obs: str = ""
    
    def set_form_nodo(self, value: str):
        self.form_nodo = value
        
    def set_form_fecha(self, value: str):
        self.form_fecha = value
        
    def set_form_tipo(self, value: str):
        self.form_tipo = value
        
    def set_form_tecnico(self, value: str):
        self.form_tecnico = value
        
    def set_form_horas(self, value: str):
        self.form_horas = value
        
    def set_form_obs(self, value: str):
        self.form_obs = value
    
    def save_mock_record(self):
        """Guarda un registro simulado en memoria."""
        if not self.form_nodo or not self.form_tecnico:
            return
        
        new_record = {
            "nodo": self.form_nodo,
            "fecha": self.form_fecha,
            "tipo": self.form_tipo,
            "tecnico": self.form_tecnico,
            "horas": self.form_horas if self.form_horas else "0"
        }
        self.records.insert(0, new_record)
        
        # Limpiar formulario
        self.form_nodo = ""
        self.form_fecha = ""
        self.form_tecnico = ""
        self.form_horas = ""
        self.form_obs = ""
    
    async def fetch_records(self):
        """Obtiene el historial de mantenimiento desde la API."""
        auth_token = await self.get_state(AuthState)
        token = auth_token.token
        
        if not token:
            self.records = []
            return
            
        try:
            async with httpx.AsyncClient() as client:
                # Simulamos la consulta al nodo 01 para obtener datos
                response = await client.get(
                    "http://localhost:8002/api/maintenance/node/nodo_01",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code == 200:
                    data = response.json()
                    # Formatear la fecha
                    for d in data:
                        if "fecha" in d:
                            d["fecha"] = d["fecha"][:10]
                    self.records = data
                else:
                    self.records = []
        except Exception as e:
            print(f"Error fetching maintenance: {e}")
            self.records = []
