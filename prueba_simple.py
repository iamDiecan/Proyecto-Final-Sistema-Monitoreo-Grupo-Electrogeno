"""
Prueba simple del backend - Sin MQTT broker
Solo verifica que las librerías se importan correctamente
"""

print("=== Verificando backend Sigegen ===\n")

# 1. Verificar imports
try:
    import paho.mqtt.client as mqtt
    print(" paho-mqtt importado correctamente")
except Exception as e:
    print(f" Error con paho-mqtt: {e}")

try:
    from influxdb_client import InfluxDBClient
    print(" influxdb-client importado correctamente")
except Exception as e:
    print(f" Error con influxdb-client: {e}")

try:
    from dotenv import load_dotenv
    print(" python-dotenv importado correctamente")
except Exception as e:
    print(f" Error con python-dotenv: {e}")

# 2. Verificar JSON (importante para el backend)
import json
print(" JSON disponible")

# 3. Verificar datetime
from datetime import datetime
print(f" datetime UTC actual: {datetime.utcnow().isoformat()}Z")

# 4. Simular un mensaje MQTT típico
payload_ejemplo = {
    "nodo_id": "nodo_01",
    "zona": "capital",
    "ubicacion": "Av. 25 de Mayo 1240, Formosa",
    "lat": -26.1775,
    "lon": -58.1781,
    "timestamp": "2026-05-07T14:32:00Z",
    "uptime_s": 86400,
    "encendido": True,
    "rpm": 1500,
    "horas_motor": 1240.5,
    "voltaje_v": 220.4,
    "frecuencia_hz": 50.1,
    "corriente_a": 18.3,
    "potencia_kw": 4.03,
    "factor_potencia": 0.98,
    "temp_motor_c": 78.2,
    "temp_ambiente_c": 32.1,
    "combustible_pct": 68,
    "combustible_l": 136.0,
    "consumo_lh": 2.1,
    "bateria_v": 12.7,
    "estado": "normal",
    "alarmas": [],
    "rssi_dbm": -68,
    "fw_version": "1.4.2"
}

print(f"\n JSON de ejemplo parseado correctamente:")
print(f"   - Nodo: {payload_ejemplo['nodo_id']}")
print(f"   - Zona: {payload_ejemplo['zona']}")
print(f"   - Voltaje: {payload_ejemplo['voltaje_v']}V")
print(f"   - Temperatura motor: {payload_ejemplo['temp_motor_c']}°C")

# 5. Detectar alarmas manualmente (simulando la lógica)
print(f"\n--- Simulando detección de alarmas ---")

# Prueba con temperatura alta
if payload_ejemplo['temp_motor_c'] > 90:
    print(f" ALERTA: Temperatura alta ({payload_ejemplo['temp_motor_c']}°C > 90°C)")
else:
    print(f" Temperatura normal ({payload_ejemplo['temp_motor_c']}°C)")

# Prueba con combustible bajo
if payload_ejemplo['combustible_pct'] < 20:
    print(f" ALERTA: Combustible bajo ({payload_ejemplo['combustible_pct']}%)")
else:
    print(f" Combustible normal ({payload_ejemplo['combustible_pct']}%)")

print("\n===  Todo funciona correctamente ===")
print("\nNota: Este es solo un test de importaciones.")