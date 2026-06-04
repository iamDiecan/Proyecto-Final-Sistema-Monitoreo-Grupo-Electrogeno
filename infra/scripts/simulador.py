import paho.mqtt.client as mqtt
import json, time, random
BROKER = "100.91.59.9"
PORT = 1883
USER = "iot_user"
PASS = "sigegen2026"
client = mqtt.Client()
client.username_pw_set("iot_user", "sigegen2026")
client.connect(BROKER, PORT)
client.loop_start()
print("Simulador arrancado — 30 generadores publicando cada 5s")
while True:
    for i in range(1, 31):
        gen_id = f"GEN_{i:02d}"
        payload = {
            "generador_id": gen_id,
            "ubicacion": f"zona_{(i % 5) + 1}",
            "temperatura": round(random.uniform(60, 120), 2),
            "rpm": round(random.uniform(1400, 1600), 2),
            "combustible": round(random.uniform(10, 100), 2)
        }
        client.publish(f"sigegen/generadores/{gen_id}", json.dumps(payload))
    time.sleep(5)