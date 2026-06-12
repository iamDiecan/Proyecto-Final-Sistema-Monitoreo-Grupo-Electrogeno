# sigen/state/admin_state.py
import reflex as rx
import asyncio
from datetime import datetime
from typing import List, Dict, Any

class AdminState(rx.State):
    """Estado local para la página de Administración (Mocks)."""
    
    users: List[Dict[str, str]] = [
        {"username": "admin", "role": "Admin", "email": "admin@sigen.com"},
        {"username": "operador_1", "role": "Operador", "email": "op1@sigen.com"}
    ]
    
    new_username: str = ""
    new_email: str = ""
    new_role: str = "Operador"
    new_password: str = ""
    
    def set_new_username(self, value: str):
        self.new_username = value
        
    def set_new_email(self, value: str):
        self.new_email = value
        
    def set_new_role(self, value: str):
        self.new_role = value
        
    def set_new_password(self, value: str):
        self.new_password = value
    
    is_backing_up: bool = False
    last_backup_time: str = "Hoy, 03:00 AM"
    
    def save_user(self):
        if not self.new_username or not self.new_role:
            return rx.window_alert("Por favor complete los campos obligatorios.")
        
        self.users.append({
            "username": self.new_username,
            "role": self.new_role,
            "email": self.new_email
        })
        
        # Reset form
        self.new_username = ""
        self.new_email = ""
        self.new_role = "Operador"
        self.new_password = ""
        return rx.window_alert("Usuario creado exitosamente (Simulado).")
        
    async def force_backup(self):
        self.is_backing_up = True
        yield
        
        await asyncio.sleep(2) # Simular carga
        
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.last_backup_time = f"Hoy, {datetime.now().strftime('%H:%M:%S')}"
        self.is_backing_up = False
        yield rx.window_alert(f"Backup completado: backup_{now}.zip")
