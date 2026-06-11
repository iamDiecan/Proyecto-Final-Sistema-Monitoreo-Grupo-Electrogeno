import reflex as rx
import httpx
from typing import Dict, Any
from sigen.state.auth_state import AuthState

class KpiState(rx.State):
    """Estado global para KPIs Operativos."""
    data: Dict[str, Any] = {
        "disponibilidad": 0.0,
        "disponibilidad_trend": "+0.0",
        "mtbf_horas": 0,
        "mtbf_trend": "+0",
        "mttr_horas": 0.0,
        "mttr_trend": "-0.0",
        "consumo_promedio_lh": 0.0,
        "consumo_trend": "-0.0",
    }
    
    @rx.var
    def disp_positive(self) -> bool:
        return float(str(self.data.get("disponibilidad_trend", "0")).replace("+", "")) >= 0

    @rx.var
    def mtbf_positive(self) -> bool:
        return float(str(self.data.get("mtbf_trend", "0")).replace("+", "")) >= 0
        
    @rx.var
    def mttr_positive(self) -> bool:
        return float(str(self.data.get("mttr_trend", "0")).replace("+", "")) <= 0 # Menor mttr es mejor

    @rx.var
    def consumo_positive(self) -> bool:
        return float(str(self.data.get("consumo_trend", "0")).replace("+", "")) <= 0 # Menor consumo es mejor
        
    @rx.var
    def trend_data(self) -> list:
        return self.data.get("trend_data", [])

    async def fetch_kpi(self):
        auth_token = await self.get_state(AuthState)
        token = auth_token.token
        
        if not token:
            return
            
        try:
            from sigen.state.auth_state import API_BASE_URL
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{API_BASE_URL}/api/kpi/",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code == 200:
                    self.data = response.json()
        except Exception as e:
            print(f"Error fetching kpis: {e}")
