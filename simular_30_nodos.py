"""
Simulador de 30 generadores para la provincia de Formosa
Cada nodo tiene características diferentes según su zona
"""

import json
import time
import random
import paho.mqtt.client as mqtt
from datetime import datetime
import sys

# Forzar codificación UTF-8 para stdout en Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass



# CONFIGURACIÓN DE NODOS POR ZONA


NODOS = []

# Zona Capital (nodos urbanos - mayor demanda)
ciudades_capital = [
    "Formosa Capital", "San Francisco de Laishi", "Villa del Carmen",
    "Gran Guardia", "Mariano Boedo", "Colonia Pastoril"
]

# Zona Norte (nodos rurales - menos demanda, más remotos)
ciudades_norte = [
    "Clorinda", "Pilcomayo", "Laguna Blanca", "Palo Santo",
    "Comandante Fontana", "El Colorado", "Ibarreta", "Estanislao del Campo",
    "Pirané", "Misión Tacaaglé"
]

# Zona Sur (nodos mixtos)
ciudades_sur = [
    "Laguna Yema", "Las Lomitas", "Pozo del Tigre", "Villa General Güemes",
    "El Espinillo", "Buena Vista", "Subteniente Perín", "San Martín II",
    "Bartolomé de las Casas", "Posta Cambio A Zalazar", "Colonia Cano",
    "Portón Negro", "Ingeniero Guillermo N. Juárez", "Frontera"
]

# Crear nodos con ubicaciones reales
nodo_id = 1
for ciudad in ciudades_capital:
    NODOS.append({
        "id": f"nodo_{nodo_id:02d}",
        "zona": "capital",
        "ubicacion": ciudad,
        "lat": -26.18 + random.uniform(-0.5, 0.5),
        "lon": -58.18 + random.uniform(-0.5, 0.5),
        "tipo": "urbano"
    })
    nodo_id += 1

for ciudad in ciudades_norte:
    NODOS.append({
        "id": f"nodo_{nodo_id:02d}",
        "zona": "norte",
        "ubicacion": ciudad,
        "lat": -25.5 + random.uniform(-0.8, 0.8),
        "lon": -58.0 + random.uniform(-0.8, 0.8),
        "tipo": "rural"
    })
    nodo_id += 1

for ciudad in ciudades_sur:
    NODOS.append({
        "id": f"nodo_{nodo_id:02d}",
        "zona": "sur",
        "ubicacion": ciudad,
        "lat": -26.5 + random.uniform(-0.5, 0.5),
        "lon": -59.0 + random.uniform(-0.5, 0.5),
        "tipo": "mixto"
    })
    nodo_id += 1

# Asegurar exactamente 30 nodos
NODOS = NODOS[:30]


# FUNCIONES PARA GENERAR DATOS REALISTAS


def generar_temp_motor(tipo_zona, estado_base):
    """
    Temperatura del motor:
    - Urbano: mayor demanda, más calor
    - Rural: menos demanda
    - Normal: 70-85°C
    - Alerta: 85-95°C
    - Crítico: 95-110°C
    """
    if estado_base == "critico":
        return random.uniform(95, 108)
    elif estado_base == "alerta":
        return random.uniform(85, 95)
    elif estado_base == "precaucion":
        return random.uniform(78, 88)
    else:
        if tipo_zona == "urbano":
            return random.uniform(70, 85)
        else:
            return random.uniform(65, 80)

def generar_voltaje(estado_base):
    """Voltaje: normal 210-230V"""
    if estado_base == "critico":
        return random.uniform(180, 200)
    elif estado_base == "alerta":
        return random.uniform(200, 210)
    elif estado_base == "precaucion":
        return random.uniform(210, 215)
    else:
        return random.uniform(215, 228)

def generar_combustible(estado_base, horas_operacion):
    """Combustible: disminuye con horas de operación"""
    base = random.uniform(70, 95)
    # Consumo según horas
    consumo = (horas_operacion % 100) / 100 * 30
    nivel = base - consumo
    
    if estado_base == "critico":
        return max(0, random.uniform(0, 10))
    elif estado_base == "alerta":
        return random.uniform(10, 25)
    elif estado_base == "precaucion":
        return random.uniform(20, 35)
    else:
        return max(25, nivel)

def generar_rpm(estado_base):
    """RPM: normal 1450-1550"""
    if estado_base == "critico":
        return random.uniform(1300, 1420)
    elif estado_base == "alerta":
        return random.uniform(1420, 1460)
    elif estado_base == "precaucion":
        return random.uniform(1460, 1480) or random.uniform(1520, 1550)
    else:
        return random.uniform(1470, 1530)

def generar_estado_aleatorio():
    """Distribución realista de estados:
    - 70% normal
    - 15% precaución
    - 10% alerta
    - 5% crítico
    """
    r = random.random()
    if r < 0.70:
        return "normal"
    elif r < 0.85:
        return "precaucion"
    elif r < 0.95:
        return "alerta"
    else:
        return "critico"


# SIMULADOR PRINCIPAL


class SimuladorGeneradores:
    def __init__(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.connect("localhost", 1883)
        self.horas_operacion = {}
        
        # Inicializar horas de operación para cada nodo
        for nodo in NODOS:
            self.horas_operacion[nodo["id"]] = random.randint(100, 5000)
    
    def generar_lectura(self, nodo):
        """Genera una lectura realista para un nodo"""
        
        # Determinar estado base (simulando condiciones reales)
        estado_base = generar_estado_aleatorio()
        
        # Ajustar según zona (nodos rurales tienen más fallas por distancia)
        if nodo["tipo"] == "rural" and estado_base == "normal":
            # Más probabilidad de fallas en zonas rurales
            if random.random() < 0.2:
                estado_base = "precaucion"
        
        # Incrementar horas de operación
        self.horas_operacion[nodo["id"]] += 0.1  # 6 minutos por ciclo
        
        # Generar valores según estado
        lectura = {
            "nodo_id": nodo["id"],
            "zona": nodo["zona"],
            "ubicacion": nodo["ubicacion"],
            "lat": nodo["lat"],
            "lon": nodo["lon"],
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "uptime_s": int(self.horas_operacion[nodo["id"]] * 3600),
            "encendido": True,
            "rpm": generar_rpm(estado_base),
            "horas_motor": round(self.horas_operacion[nodo["id"]], 1),
            "voltaje_v": round(generar_voltaje(estado_base), 1),
            "frecuencia_hz": round(random.uniform(49.5, 50.5), 1),
            "corriente_a": round(random.uniform(10, 25), 1),
            "potencia_kw": round(random.uniform(3, 8), 2),
            "factor_potencia": round(random.uniform(0.85, 0.99), 2),
            "temp_motor_c": round(generar_temp_motor(nodo["tipo"], estado_base), 1),
            "temp_ambiente_c": round(random.uniform(25, 40), 1),
            "combustible_pct": round(generar_combustible(estado_base, self.horas_operacion[nodo["id"]]), 1),
            "combustible_l": round(random.uniform(50, 200), 1),
            "consumo_lh": round(random.uniform(1.5, 3.5), 1),
            "bateria_v": round(random.uniform(11.5, 13.5), 1),
            "rssi_dbm": random.randint(-85, -50),
            "fw_version": "1.4.2"
        }
        
        return lectura
    
    def publicar_todos(self):
        """Publica lecturas de todos los nodos"""
        print("\n" + "="*80)
        print("SIMULACIÓN DE 30 GENERADORES - PROVINCIA DE FORMOSA")
        print("="*80)
        
        for nodo in NODOS:
            lectura = self.generar_lectura(nodo)
            topic = f"sigegen/{lectura['zona']}/{lectura['nodo_id']}/datos"
            payload = json.dumps(lectura)
            
            self.client.publish(topic, payload)
            
            # Mostrar resumen
            estado_icono = {
                "normal": "✅",
                "precaucion": "⚠️",
                "alerta": "🔶",
                "critico": "🔴"
            }
            nivel_estado = self._estimar_nivel(lectura)
            icono = estado_icono.get(nivel_estado, "❓")
            
            print(f"{icono} {lectura['nodo_id']} | {lectura['zona']:8} | "
                  f"{lectura['ubicacion']:25} | "
                  f"T:{lectura['temp_motor_c']:3.0f}°C | "
                  f"V:{lectura['voltaje_v']:3.0f}V | "
                  f"C:{lectura['combustible_pct']:3.0f}%")
            
            # Pequeña pausa para no saturar
            time.sleep(0.05)
        
        print("\n" + "="*80)
        print(f" Publicados {len(NODOS)} mensajes")
        print("="*80)
    
    def _estimar_nivel(self, lectura):
        """Estimación rápida del nivel (para mostrar en consola)"""
        temp = lectura['temp_motor_c']
        volt = lectura['voltaje_v']
        comb = lectura['combustible_pct']
        
        if temp > 95 or volt < 200 or comb < 15:
            return "critico"
        elif temp > 85 or volt < 210 or comb < 25:
            return "alerta"
        elif temp > 78 or volt < 215 or comb < 35:
            return "precaucion"
        else:
            return "normal"
    
    def simular_ciclo(self, ciclos=1, intervalo_segundos=10):
        """Ejecuta múltiples ciclos de simulación"""
        for ciclo in range(ciclos):
            print(f"\n🔄 CICLO {ciclo + 1}/{ciclos}")
            self.publicar_todos()
            
            if ciclo < ciclos - 1:
                print(f"\n⏳ Esperando {intervalo_segundos} segundos para próximo ciclo...")
                time.sleep(intervalo_segundos)
    
    def cerrar(self):
        self.client.disconnect()



# EJECUCIÓN


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════════╗
    ║     SIGEGEN - SIMULADOR DE 30 GENERADORES - PROVINCIA DE FORMOSA     ║
    ║                                                                      ║
    ║  Simula el envío de datos desde 30 generadores distribuidos en:      ║
    ║  • Zona Capital (6 nodos urbanos)                                    ║
    ║  • Zona Norte (10 nodos rurales)                                     ║
    ║  • Zona Sur (14 nodos mixtos)                                        ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    simulador = SimuladorGeneradores()
    
    try:
        # Simular 1 ciclo completo (todos los nodos una vez)
        # Para múltiples ciclos, cambiar ciclos=3, intervalo=30
        simulador.simular_ciclo(ciclos=1, intervalo_segundos=10)
        
        print("\n✨ Simulación completada. El backend está procesando los datos.")
        print("   Podés consultar la base de datos con: sqlite3 sigegen.db")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Simulación detenida por el usuario")
    finally:
        simulador.cerrar()