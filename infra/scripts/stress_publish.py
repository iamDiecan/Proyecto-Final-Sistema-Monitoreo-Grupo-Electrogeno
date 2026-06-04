"""
SIGEGEN - Generador de carga MQTT (stress test)
================================================
Publica datos de N generadores simulados a un intervalo configurable,
para medir hasta dónde aguanta el pipeline (broker -> puente -> InfluxDB).

CORRELO DESDE EL LENOVO O LA JUANA MANSO, **no** desde la VM:
así la CPU del que genera la carga no le compite a lo que estás midiendo.

Ejemplos:
    python stress_publish.py --generators 100 --interval 5 --duration 300 --password TU_PASS
    python stress_publish.py --generators 300 --interval 5 --duration 300 --password TU_PASS
    python stress_publish.py --generators 30  --interval 0.5 --duration 180 --password TU_PASS

Mirá la "tasa_real": si queda por debajo de la objetivo, el cuello de botella
es el generador (esta PC), no el servidor. En ese caso, subí la PC o repartí
la carga en dos máquinas.
"""

import argparse
import json
import time
import random
import paho.mqtt.client as mqtt

parser = argparse.ArgumentParser(description="SIGEGEN - generador de carga MQTT")
parser.add_argument("--generators", type=int, default=30, help="cantidad de generadores simulados")
parser.add_argument("--interval", type=float, default=5.0, help="segundos entre rondas de publicacion")
parser.add_argument("--duration", type=int, default=60, help="duracion del test en segundos (0 = infinito)")
parser.add_argument("--host", default="100.91.59.9", help="IP del broker (Netbird)")
parser.add_argument("--port", type=int, default=1883)
parser.add_argument("--user", default="iot_user")
parser.add_argument("--password", default="TU_PASSWORD")
args = parser.parse_args()

client = mqtt.Client()
client.username_pw_set(args.user, args.password)
client.connect(args.host, args.port)
client.loop_start()

objetivo = args.generators / args.interval
print(f"Stress: {args.generators} generadores cada {args.interval}s "
      f"= {objetivo:.1f} msg/s objetivo, durante {args.duration or 'infinito'}s")

enviados = 0
inicio = time.time()
try:
    while True:
        ronda = time.time()
        for i in range(1, args.generators + 1):
            gen_id = f"GEN_{i:03d}"
            payload = {
                "generador_id": gen_id,
                "ubicacion": f"zona_{(i % 5) + 1}",
                "temperatura": round(random.uniform(60, 120), 2),
                "rpm": round(random.uniform(1400, 1600), 2),
                "combustible": round(random.uniform(10, 100), 2),
            }
            client.publish(f"sigegen/generadores/{gen_id}", json.dumps(payload))
            enviados += 1

        transcurrido = time.time() - inicio
        print(f"[{transcurrido:6.1f}s] enviados={enviados:<7d} "
              f"tasa_real={enviados / transcurrido:6.1f} msg/s")

        if args.duration and transcurrido >= args.duration:
            break

        resto = args.interval - (time.time() - ronda)
        if resto > 0:
            time.sleep(resto)
except KeyboardInterrupt:
    print("\nDetenido por usuario.")
finally:
    client.loop_stop()
    client.disconnect()
    total = time.time() - inicio
    print(f"\nTotal: {enviados} mensajes en {total:.1f}s = {enviados / total:.1f} msg/s promedio")
