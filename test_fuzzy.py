import json
import paho.mqtt.client as mqtt
import time

# Datos de prueba con diferentes niveles de severidad
casos = [
    # Caso 1: Normal
    {"nodo_id": "nodo_01", "temp_motor_c": 65, "voltaje_v": 220, "combustible_pct": 80, "rpm": 1500},
    # Caso 2: Precaución
    {"nodo_id": "nodo_02", "temp_motor_c": 85, "voltaje_v": 215, "combustible_pct": 60, "rpm": 1480},
    # Caso 3: Alerta
    {"nodo_id": "nodo_03", "temp_motor_c": 95, "voltaje_v": 205, "combustible_pct": 40, "rpm": 1460},
    # Caso 4: Crítico
    {"nodo_id": "nodo_04", "temp_motor_c": 105, "voltaje_v": 200, "combustible_pct": 15, "rpm": 1420},
]

client = mqtt.Client()
client.connect("localhost", 1883)

for caso in casos:
    caso["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    payload = json.dumps(caso)
    topic = f"sigegen/capital/{caso['nodo_id']}/datos"
    client.publish(topic, payload)
    print(f"Enviado: {topic} -> {payload}")
    time.sleep(2)

client.disconnect()
print("Prueba completada")