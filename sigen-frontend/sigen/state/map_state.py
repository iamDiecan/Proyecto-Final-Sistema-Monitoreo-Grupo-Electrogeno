# sigen-frontend/sigen/state/map_state.py
import reflex as rx
import httpx
import json
from typing import List, Dict, Any
from sigen.state.auth_state import AuthState

class MapState(rx.State):
    """Estado global para el Mapa Provincial."""
    nodes: List[Dict[str, Any]] = []
    
    async def fetch_nodes(self):
        """Obtiene las coordenadas y estados de todos los nodos."""
        auth_token = await self.get_state(AuthState)
        token = auth_token.token
        
        if not token:
            self.nodes = []
            return
            
        try:
            from sigen.state.auth_state import API_BASE_URL
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{API_BASE_URL}/api/map/nodes",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code == 200:
                    self.nodes = response.json()
                    yield rx.call_script(
                        f"if (typeof window.updateMapMarkers === 'function') window.updateMapMarkers({json.dumps(self.nodes)})"
                    )
                else:
                    self.nodes = []
        except Exception as e:
            print(f"Error fetching map nodes: {e}")
            self.nodes = []
