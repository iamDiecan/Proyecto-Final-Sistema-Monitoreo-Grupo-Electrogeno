# sigen/state/generador_state.py
"""
Estado global de SIGEGEN para Reflex.
Maneja la obtención de datos desde el backend FastAPI,
el estado de conexión a InfluxDB, filtros de UI y auto-refresco.
"""
import reflex as rx
import httpx
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

API_BASE_URL = "http://localhost:8001"

# Timeout configurado para llamadas HTTP (en segundos)
HTTP_TIMEOUT = httpx.Timeout(timeout=10.0, connect=5.0)


def format_generator_data(g: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to pre-format generator telemetry data into display-friendly values."""
    g = dict(g)
    
    # 1. Format basic fields for display
    nodo_id = g.get("nodo_id", "nodo_00")
    g["nodo_numero"] = nodo_id.split('_')[1] if '_' in nodo_id else nodo_id
    g["ubicacion"] = g.get("ubicacion", "Sin ubicación")
    g["nombre_completo"] = f"{nodo_id} - {g['ubicacion']}"
    
    zona = g.get("zona", "desconocida")
    g["zona_upper"] = zona.upper()
    g["zona_friendly"] = f"Zona: {zona.upper()}"
    
    estado = g.get("estado", "normal")
    g["estado_upper"] = estado.upper()
    
    # 2. Format sensor telemetry values
    voltaje = g.get("voltaje_v")
    g["voltaje_str"] = f"{voltaje:.1f} V" if voltaje is not None else "0.0 V"
    g["voltaje_friendly"] = g["voltaje_str"]
    
    temp = g.get("temp_motor_c")
    g["temp_motor_str"] = f"{temp:.1f} °C" if temp is not None else "0.0 °C"
    g["temp_motor_friendly"] = g["temp_motor_str"]
    
    freq = g.get("frecuencia_hz")
    g["frecuencia_friendly"] = f"{freq:.1f} Hz" if freq is not None else "0.0 Hz"
    
    corr = g.get("corriente_a")
    g["corriente_friendly"] = f"{corr:.1f} A" if corr is not None else "0.0 A"
    
    pot = g.get("potencia_kw")
    g["potencia_friendly"] = f"{pot:.1f} kW" if pot is not None else "0.0 kW"
    
    fp = g.get("factor_potencia")
    g["factor_potencia_friendly"] = f"{fp:.2f}" if fp is not None else "0.00"
    
    rpm = g.get("rpm")
    g["rpm_friendly"] = f"{rpm:.0f} RPM" if rpm is not None else "0 RPM"
    
    horas = g.get("horas_motor")
    g["horas_motor_friendly"] = f"{horas:.1f} hs" if horas is not None else "0.0 hs"
    
    bat = g.get("bateria_v")
    g["bateria_friendly"] = f"{bat:.1f} V" if bat is not None else "0.0 V"
    
    uptime = g.get("uptime_s", 0)
    g["uptime_friendly"] = f"{int(uptime // 3600)} horas"
    
    rssi = g.get("rssi_dbm")
    g["rssi_str"] = f"{rssi} dBm" if rssi is not None else "0 dBm"
    g["rssi_friendly"] = g["rssi_str"]
    
    fw = g.get("fw_version", "v1.0")
    g["firmware_friendly"] = f"Firmware: {fw}"
    
    # 3. Fuel fields
    comb = g.get("combustible_pct")
    g["combustible_str"] = f"{comb:.0f}%" if comb is not None else "0%"
    
    comb_l = g.get("combustible_l", 0.0)
    g["combustible_capacidad_friendly"] = f"{comb:.0f}% ({comb_l:.1f} L)" if comb is not None else f"0% ({comb_l:.1f} L)"
    
    consumo = g.get("consumo_lh", 0.0)
    g["consumo_friendly"] = f"{consumo:.1f} L/h"
    
    autonomia = comb_l / consumo if consumo > 0.0 else 0.0
    g["autonomia_friendly"] = f"{autonomia:.1f} hs"
    
    # 4. Alerta difusa fields
    alerta_lvl = g.get("alerta_difusa_nivel", 0.0)
    g["alerta_nivel_str"] = f"{alerta_lvl:.1f} / 100"
    g["alerta_difusa_nivel_friendly"] = f"{alerta_lvl:.1f}%"
    
    categoria = g.get("alerta_difusa_categoria", "normal")
    g["alerta_difusa_categoria_friendly"] = f"Severidad: {categoria.upper()}"
    
    # Contributions (decompress and handle)
    contrib = g.get("alerta_difusa_contribuciones", {})
    if isinstance(contrib, str):
        try:
            contrib = json.loads(contrib)
        except:
            contrib = {}
    
    # We populate direct contrib values
    g["temp_contrib"] = float(contrib.get("temp", contrib.get("temperatura", 0.0)))
    g["volt_contrib"] = float(contrib.get("voltaje", 0.0))
    g["comb_contrib"] = float(contrib.get("combustible", 0.0))
    g["rpm_contrib"] = float(contrib.get("rpm", 0.0))
    
    g["temp_contrib_str"] = f"{g['temp_contrib']:.0f}%"
    g["volt_contrib_str"] = f"{g['volt_contrib']:.0f}%"
    g["comb_contrib_str"] = f"{g['comb_contrib']:.0f}%"
    g["rpm_contrib_str"] = f"{g['rpm_contrib']:.0f}%"
    
    # 5. Dynamic Colors & borders based on state/alert level
    color_map = {
        "normal": "#10B981",
        "precaucion": "#F59E0B",
        "alerta": "#F97316",
        "falla": "#EF4444",
        "emergencia": "#EF4444"
    }
    bg_map = {
        "normal": "rgba(16, 185, 129, 0.15)",
        "precaucion": "rgba(245, 158, 11, 0.15)",
        "alerta": "rgba(249, 115, 22, 0.15)",
        "falla": "rgba(239, 68, 68, 0.15)",
        "emergencia": "rgba(239, 68, 68, 0.15)"
    }
    color = color_map.get(categoria, "#10B981")
    g["alert_color"] = color
    g["alert_bg"] = bg_map.get(categoria, "rgba(16, 185, 129, 0.15)")
    g["alert_border_hover"] = f"1px solid {color}30"
    
    # 6. Timestamp friendly formatting
    ts_raw = g.get("timestamp", "")
    ts_friendly = ts_raw
    if "T" in ts_raw:
        try:
            fecha, hora = ts_raw.split("T")
            hora_clean = hora.split(".")[0] if "." in hora else hora.split("Z")[0]
            ts_friendly = f"{fecha} | {hora_clean}"
        except:
            pass
    g["timestamp_friendly"] = ts_friendly
    
    # Alarmas traditional check
    alarmas = g.get("alarmas", [])
    if isinstance(alarmas, str):
        try:
            alarmas = json.loads(alarmas)
        except:
            alarmas = []
    g["alarmas"] = [str(a) for a in alarmas]
    g["has_alarmas"] = len(alarmas) > 0
    
    return g

class GeneradorState(rx.State):
    """Estado global para manejar el flujo de datos de SIGEGEN."""
    
    # Datos cargados de la API
    generadores: List[Dict[str, Any]] = []
    alertas: List[Dict[str, Any]] = []
    resumen: Dict[str, Any] = {
        "total": 0,
        "encendidos": 0,
        "apagados": 0,
        "normal": 0,
        "alerta": 0,
        "falla": 0,
        "alerta_promedio": 0.0,
        "combustible_promedio": 0.0
    }
    
    # Detalle de generador seleccionado
    selected_generador: Dict[str, Any] = {}
    historial_telemetria: List[Dict[str, Any]] = []
    selected_generador_id: str = ""
    
    # Filtros de UI
    filtro_busqueda: str = ""
    filtro_zona: str = ""   # "", "capital", "norte", "sur"
    filtro_estado: str = "" # "", "normal", "alerta", "falla"
    
    # Estado de UI
    loading: bool = False
    loading_detail: bool = False
    error: str = ""
    
    # Estado de conexión InfluxDB
    is_influx_connected: bool = False
    datasource_mode: str = ""  # "influxdb", "sqlite_fallback", "no_datasource"
    last_refresh: str = ""
    
    # Temporizador de auto-refresco (en segundos)
    refresh_counter: int = 0

    @rx.var
    def total_generadores(self) -> str:
        return str(self.resumen.get("total", 0))

    @rx.var
    def alerta_promedio_str(self) -> str:
        return f"{self.resumen.get('alerta_promedio', 0.0):.1f}%"

    @rx.var
    def falla_generadores(self) -> str:
        return str(self.resumen.get("falla", 0))

    @rx.var
    def combustible_promedio_str(self) -> str:
        return f"{self.resumen.get('combustible_promedio', 0.0):.1f}%"

    @rx.var
    def resumen_subtitulo_totales(self) -> str:
        return f"{self.resumen.get('encendidos', 0)} Activos / {self.resumen.get('apagados', 0)} Apagados"

    @rx.var
    def has_error(self) -> bool:
        """Indica si hay un error activo para mostrar en la UI."""
        return len(self.error) > 0

    @rx.var
    def influx_status_text(self) -> str:
        """Texto descriptivo del estado de la fuente de datos."""
        if self.datasource_mode == "influxdb":
            return "InfluxDB Conectado"
        elif self.datasource_mode == "sqlite_fallback":
            return "SQLite (Fallback)"
        elif self.datasource_mode == "no_datasource":
            return "Sin conexión"
        return "Verificando..."

    @rx.var
    def influx_status_color(self) -> str:
        """Color del badge de conexión."""
        if self.datasource_mode == "influxdb":
            return "green"
        elif self.datasource_mode == "sqlite_fallback":
            return "yellow"
        return "red"

    @rx.var
    def generadores_filtrados(self) -> List[Dict[str, Any]]:
        """Aplica filtros en tiempo real sobre la lista de generadores."""
        resultado = []
        for g in self.generadores:
            # Filtro por búsqueda de ubicación o ID
            match_busqueda = True
            if self.filtro_busqueda:
                termino = self.filtro_busqueda.lower()
                id_match = termino in g.get("nodo_id", "").lower()
                loc_match = termino in g.get("ubicacion", "").lower()
                match_busqueda = id_match or loc_match
            
            # Filtro por zona
            match_zona = True
            if self.filtro_zona:
                match_zona = g.get("zona", "").lower() == self.filtro_zona.lower()
                
            # Filtro por estado
            match_estado = True
            if self.filtro_estado:
                match_estado = g.get("estado", "").lower() == self.filtro_estado.lower()
                
            if match_busqueda and match_zona and match_estado:
                resultado.append(g)
        return resultado

    def set_filtro_busqueda(self, valor: str):
        self.filtro_busqueda = valor

    def set_filtro_zona(self, valor: str):
        self.filtro_zona = valor

    def set_filtro_estado(self, valor: str):
        self.filtro_estado = valor

    async def check_health(self):
        """Verifica el estado de salud del backend y la conexión a InfluxDB."""
        try:
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
                response = await client.get(f"{API_BASE_URL}/health")
                if response.status_code == 200:
                    data = response.json()
                    self.is_influx_connected = data.get("influxdb") == "connected"
                    self.datasource_mode = data.get("mode", "")
                else:
                    self.is_influx_connected = False
                    self.datasource_mode = "no_datasource"
        except httpx.ConnectError:
            self.is_influx_connected = False
            self.datasource_mode = "no_datasource"
            self.error = "No se pudo conectar con el servidor backend. Verifique que esté corriendo en el puerto 8001."
        except httpx.TimeoutException:
            self.is_influx_connected = False
            self.datasource_mode = "no_datasource"
            self.error = "Timeout al conectar con el backend. El servidor tardó demasiado en responder."
        except Exception as e:
            self.is_influx_connected = False
            self.datasource_mode = "no_datasource"

    async def cargar_resumen(self):
        """Obtiene las métricas de resumen global de la API."""
        try:
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
                response = await client.get(f"{API_BASE_URL}/api/resumen")
                if response.status_code == 200:
                    self.resumen = response.json()
        except httpx.ConnectError:
            self.error = "Error de conexión con la API al cargar resumen."
        except httpx.TimeoutException:
            self.error = "Timeout al cargar resumen del dashboard."
        except Exception as e:
            self.error = f"Error de conexión con la API: {str(e)}"

    async def cargar_generadores(self):
        """Obtiene la lista completa de generadores con su telemetría más reciente."""
        self.loading = True
        try:
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
                response = await client.get(f"{API_BASE_URL}/api/generadores")
                if response.status_code == 200:
                    self.generadores = [format_generator_data(g) for g in response.json()]
                    self.error = ""
                else:
                    self.error = f"Error del servidor backend ({response.status_code})"
        except httpx.ConnectError:
            self.error = "No se pudo conectar con el servidor backend."
        except httpx.TimeoutException:
            self.error = "Timeout al cargar lista de generadores."
        except Exception as e:
            self.error = f"Error al cargar generadores: {str(e)}"
        finally:
            self.loading = False

    async def cargar_alertas(self):
        """Obtiene el historial de alertas recientes."""
        try:
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
                response = await client.get(f"{API_BASE_URL}/api/alertas?limite=30")
                if response.status_code == 200:
                    self.alertas = [format_generator_data(a) for a in response.json()]
        except httpx.ConnectError:
            print("Error de conexión al cargar alertas")
        except httpx.TimeoutException:
            print("Timeout al cargar alertas")
        except Exception as e:
            print(f"Error cargando alertas: {e}")

    async def cargar_todos_datos(self):
        """Carga en paralelo todos los datos de inicio."""
        await self.check_health()
        await self.cargar_resumen()
        await self.cargar_generadores()
        await self.cargar_alertas()
        # Actualizar timestamp de última carga
        self.last_refresh = datetime.now().strftime("%H:%M:%S")

    async def periodic_refresh(self):
        """Función periódica gatillada por Reflex para auto-refrescar datos en vivo."""
        self.refresh_counter += 1
        await self.check_health()
        await self.cargar_resumen()
        await self.cargar_generadores()
        await self.cargar_alertas()
        self.last_refresh = datetime.now().strftime("%H:%M:%S")
        
        # Si hay un generador detallado actualmente seleccionado, refrescar sus datos también
        if self.selected_generador_id:
            await self.cargar_detalle(self.selected_generador_id)

    async def cargar_detalle(self, generador_id: str):
        """Carga la telemetría detallada e histórica de un generador en particular."""
        self.selected_generador_id = generador_id
        self.loading_detail = True
        try:
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
                # 1. Obtener última lectura del nodo
                response_ultimo = await client.get(f"{API_BASE_URL}/api/telemetria/{generador_id}/ultimo")
                if response_ultimo.status_code == 200:
                    self.selected_generador = format_generator_data(response_ultimo.json())
                
                # 2. Obtener historial para gráficos
                response_historial = await client.get(f"{API_BASE_URL}/api/telemetria/{generador_id}/historial?limite=30")
                if response_historial.status_code == 200:
                    self.historial_telemetria = [format_generator_data(h) for h in response_historial.json()]
                    # Limpiar timestamps para que se vean amigables en el gráfico
                    for h in self.historial_telemetria:
                        if "timestamp" in h:
                            try:
                                # ISO string a Hora:Minuto:Segundo
                                dt = h["timestamp"].split("T")[1][:5]
                                h["hora"] = dt
                            except:
                                h["hora"] = h["timestamp"]
        except httpx.ConnectError:
            self.error = "Error de conexión al cargar detalle del generador."
        except httpx.TimeoutException:
            self.error = "Timeout al cargar detalle del generador."
        except Exception as e:
            self.error = f"Error cargando detalle: {str(e)}"
        finally:
            self.loading_detail = False

    async def cargar_detalle_por_id(self):
        """Saca el ID del generador del parámetro de ruta e inicia la carga."""
        # Reflex provee el router param con self.router.page.params
        gen_id = self.router.page.params.get("id")
        if gen_id:
            await self.cargar_detalle(gen_id)
        else:
            self.error = "ID de generador no proveído en la URL"

    def ir_a_detalle(self, generador_id: str):
        """Navega a la vista de detalle de un generador específico."""
        return rx.redirect(f"/generador/{generador_id}")

    def dismiss_error(self):
        """Limpia el mensaje de error actual."""
        self.error = ""