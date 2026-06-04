"""
latency_probe.py — mide la latencia de ida y vuelta por el broker MQTT.

Publica mensajes-sonda con un numero de secuencia y, como esta suscripto al
mismo topic, mide cuanto tarda cada uno en volver: publicado -> broker ->
entregado. Como el envio y la recepcion ocurren en el MISMO proceso (mismo
reloj), no hay desfasaje de relojes entre maquinas: la medicion es limpia.

Metodologia:
  1) Corrélo contra el broker OCIOSO  -> baseline de latencia.
  2) Corrélo de nuevo mientras stress_publish.py mete carga -> latencia bajo carga.
  3) Compará los percentiles (P50/P95/P99) entre los dos.

Ojo: el probe manda pocos mensajes a baja frecuencia a proposito, asi el que
mide no agrega carga. La carga la pone stress_publish.py.

Mide la latencia de TRANSPORTE (capa MQTT). El guardado en InfluxDB suma
ademas el flush por lotes (hasta flush_interval = 1s con la config actual).

Ejemplos:
    python latency_probe.py --count 200 --interval 0.2 --password TU_PASS
"""

import argparse
import json
import time
import statistics
import paho.mqtt.client as mqtt

parser = argparse.ArgumentParser(description="SIGEGEN - probe de latencia MQTT")
parser.add_argument("--count", type=int, default=200, help="cantidad de sondas")
parser.add_argument("--interval", type=float, default=0.2, help="segundos entre sondas")
parser.add_argument("--host", default="100.91.59.9")
parser.add_argument("--port", type=int, default=1883)
parser.add_argument("--user", default="iot_user")
parser.add_argument("--password", default="TU_PASSWORD")
args = parser.parse_args()

TOPIC = "sigegen/_probe"   # topic aparte: el puente NO lo procesa, medimos solo el broker
latencias_ms = []
pendientes = {}            # seq -> instante de envio


def on_message(client, userdata, msg):
    t_recv = time.perf_counter()
    try:
        seq = json.loads(msg.payload)["seq"]
        t_envio = pendientes.pop(seq, None)
        if t_envio is not None:
            latencias_ms.append((t_recv - t_envio) * 1000.0)
    except Exception:
        pass


client = mqtt.Client()
client.username_pw_set(args.user, args.password)
client.on_message = on_message
client.connect(args.host, args.port)
client.subscribe(TOPIC)
client.loop_start()
time.sleep(0.5)  # dar tiempo a que la suscripcion quede activa

print(f"Sondeando {args.count} mensajes cada {args.interval}s por '{TOPIC}' ...")
for seq in range(args.count):
    pendientes[seq] = time.perf_counter()
    client.publish(TOPIC, json.dumps({"seq": seq}))
    time.sleep(args.interval)

time.sleep(2)  # esperar las ultimas respuestas
client.loop_stop()
client.disconnect()

if latencias_ms:
    latencias_ms.sort()

    def pct(p):
        idx = min(len(latencias_ms) - 1, int(len(latencias_ms) * p / 100))
        return latencias_ms[idx]

    perdidas = args.count - len(latencias_ms)
    print(f"\nMuestras: {len(latencias_ms)} de {args.count}  (sondas sin volver: {perdidas})")
    print(f"  min  : {latencias_ms[0]:7.2f} ms")
    print(f"  P50  : {pct(50):7.2f} ms")
    print(f"  P95  : {pct(95):7.2f} ms")
    print(f"  P99  : {pct(99):7.2f} ms")
    print(f"  max  : {latencias_ms[-1]:7.2f} ms")
    print(f"  prom : {statistics.mean(latencias_ms):7.2f} ms")
else:
    print("No volvio ninguna sonda. Revisá que el broker este arriba y las credenciales.")
