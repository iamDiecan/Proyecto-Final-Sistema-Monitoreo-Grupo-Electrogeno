# sigen-frontend/sigen/state/auth_state.py
import reflex as rx
import httpx

API_BASE_URL = "http://localhost:8002"

class AuthState(rx.State):
    """Estado global para la autenticación."""
    
    username: str = ""
    password: str = ""
    error_message: str = ""
    is_authenticated: bool = False
    token: str = rx.Cookie("")
    user_role: str = ""
    full_name: str = ""
    
    def set_username(self, val: str):
        self.username = val

    def set_password(self, val: str):
        self.password = val
        
    @rx.var
    def is_admin(self) -> bool:
        return self.user_role == "admin"
        
    async def login(self):
        """Realiza el login contra el backend."""
        self.error_message = ""
        try:
            async with httpx.AsyncClient() as client:
                data = {"username": self.username, "password": self.password}
                response = await client.post(
                    f"{API_BASE_URL}/api/auth/login",
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.token = result["access_token"]
                    self.is_authenticated = True
                    # Resetear form
                    self.username = ""
                    self.password = ""
                    await self.fetch_user_profile()
                    return rx.redirect("/")
                else:
                    self.error_message = "Usuario o contraseña incorrectos."
        except Exception as e:
            self.error_message = f"Error de conexión: {str(e)}"
            
    async def fetch_user_profile(self):
        """Obtiene los datos del usuario logueado."""
        if not self.token:
            return
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{API_BASE_URL}/api/auth/me",
                    headers={"Authorization": f"Bearer {self.token}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.user_role = data.get("role", "")
                    self.full_name = data.get("full_name", "")
                    self.is_authenticated = True
                else:
                    self.logout()
        except Exception:
            self.logout()

    def logout(self):
        """Cierra la sesión."""
        self.token = ""
        self.is_authenticated = False
        self.user_role = ""
        self.full_name = ""
        return rx.redirect("/login")
        
    async def check_auth(self):
        """Verifica si hay un token válido al cargar una página protegida."""
        if not self.is_authenticated and self.token:
            await self.fetch_user_profile()
            
        if not self.is_authenticated and self.router.page.path != "/login":
            # Forzamos login (comentado en desarrollo para facilitar pruebas, descomentar en prod)
            # return rx.redirect("/login")
            pass
