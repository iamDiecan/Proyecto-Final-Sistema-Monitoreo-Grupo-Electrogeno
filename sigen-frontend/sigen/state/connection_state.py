import reflex as rx
import httpx
import asyncio

class ConnectionState(rx.State):
    """Estado para verificar la conexión con el backend de FastAPI."""
    status: str = "Verificando conexión..."
    is_connected: bool = False
    
    @rx.background
    async def check_connection(self):
        while True:
            async with self:
                try:
                    # Intenta conectar con FastAPI en el puerto 8001
                    async with httpx.AsyncClient() as client:
                        response = await client.get("http://localhost:8002/health", timeout=2.0)
                        if response.status_code == 200:
                            self.status = "Conectado al backend"
                            self.is_connected = True
                        else:
                            self.status = "Sin conexión"
                            self.is_connected = False
                except Exception:
                    self.status = "Sin conexión"
                    self.is_connected = False
            
            # Reintentar cada 5 segundos
            await asyncio.sleep(5)
