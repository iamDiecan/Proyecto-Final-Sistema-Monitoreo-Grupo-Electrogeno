import reflex as rx
import httpx
from sigen.state.auth_state import AuthState, API_BASE_URL

class ConfigState(rx.State):
    """Estado para la configuración del sistema."""
    frecuencia_telemetria: int = 5
    umbral_temperatura: int = 85
    umbral_combustible: int = 20
    
    # UI state
    is_simulating: bool = False
    status_message: str = ""

    def set_frecuencia_telemetria(self, value: int):
        self.frecuencia_telemetria = int(value)
        
    def set_umbral_temperatura(self, value: int):
        self.umbral_temperatura = int(value)
        
    def set_umbral_combustible(self, value: int):
        self.umbral_combustible = int(value)

    async def trigger_simulator(self):
        """Dispara el simulador en el backend."""
        self.is_simulating = True
        self.status_message = "Iniciando simulación de datos..."
        yield
        
        auth_token = await self.get_state(AuthState)
        token = auth_token.token
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{API_BASE_URL}/api/config/simulate",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code == 200:
                    self.status_message = "¡Simulación ejecutada con éxito!"
                else:
                    self.status_message = f"Error al simular: {response.status_code}"
        except Exception as e:
            self.status_message = f"Error de conexión: {e}"
            
        self.is_simulating = False
