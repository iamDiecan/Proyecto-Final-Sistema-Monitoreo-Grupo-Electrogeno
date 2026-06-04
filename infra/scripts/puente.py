import paho.mqtt.client as mqtt
import json
from influxdb_client import InfluxDBClient, Point, WriteOptions

BROKER = "100.91.59.9"
MQTT_USER = "iot_user"
MQTT_PASS = "sigegen2026"

INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = open("/home/florencia/sigegen/token.txt").read().strip()
INFLUX_ORG = "sigegen"
INFLUX_BUCKET = "generadores"

influx = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx.write_api(write_options=WriteOptions(batch_size=500, flush_interval=1000))

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload)
        point = (Point("generador")
            .tag("generador_id", data["generador_id"])
            .tag("ubicacion", data["ubicacion"])
            .field("temperatura", data["temperatura"])
            .field("rpm", data["rpm"])
            .field("combustible", data["combustible"]))
        write_api.write(bucket=INFLUX_BUCKET, record=point)
        print(f"Escrito: {data['generador_id']}")
    except Exception as e:
        print(f"Error: {e}")

client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.on_message = on_message
client.connect(BROKER, 1883)
client.subscribe("sigegen/generadores/#")
print("Puente arrancado — escuchando MQTT y escribiendo a InfluxDB")
client.loop_forever()
