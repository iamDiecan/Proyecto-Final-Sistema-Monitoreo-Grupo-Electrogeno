# WIKI — Proyecto IoT Formosa / SIGEGEN
> Archivo central. Todo lo que necesitás en un solo lugar.
> Última actualización: 31 mayo 2026

---

## Índice

1. [¿Qué es este proyecto?](#1-qué-es-este-proyecto)
2. [Arquitectura](#2-arquitectura)
3. [Mi rol](#3-mi-rol)
4. [Hardware disponible](#4-hardware-disponible)
5. [Credenciales y datos de conexión](#5-credenciales-y-datos-de-conexión)
6. [Cómo levantar el stack](#6-cómo-levantar-el-stack)
7. [Configuraciones](#7-configuraciones)
8. [Scripts y código](#8-scripts-y-código)
9. [Errores conocidos y soluciones](#9-errores-conocidos-y-soluciones)
10. [Decisiones tomadas y por qué](#10-decisiones-tomadas-y-por-qué)
11. [Decisiones abiertas](#11-decisiones-abiertas)
12. [Pendientes y próximos pasos](#12-pendientes-y-próximos-pasos)
13. [Glosario rápido](#13-glosario-rápido)

---

## 1. ¿Qué es este proyecto?

**SIGEGEN** es un sistema de monitoreo (y posiblemente control) de una flota de generadores heterogéneos distribuidos geográficamente en la provincia de Formosa, usando IoT.

- **Entrega parcial**: junio 2026
- **Entrega final**: octubre 2026
- **Institución**: Instituto Politécnico de Formosa

### ¿Qué monitorea?

Generadores heterogéneos (distintos modelos, marcas, capacidades) en distintos puntos de Formosa. Variables típicas: temperatura, RPM, nivel de combustible. El sistema tiene que adaptarse a generadores con distintos sensores y protocolos.

---

## 2. Arquitectura

### Estado actual (stack operativo sobre red Netbird)

```
Simulador Python (Lenovo y Juana Manso — clientes externos que simulan nodos de campo)
      ↓  MQTT  topic: sigegen/generadores/GEN_XX
      ↓  sobre red Netbird (broker en 100.91.59.9:1883)
Mosquitto MQTT Broker (VM Ubuntu, servicio systemd)
      ↓  suscripción: sigegen/generadores/#
Puente Python (VM Ubuntu) — parsea JSON y escribe en InfluxDB (escritura por lotes)
      ↓
InfluxDB 2.9.1 (VM Ubuntu, servicio systemd, localhost:8086)
      ↓  consulta Flux cada 60s
Bot de Telegram (VM Ubuntu) — alertas automáticas → chat "SIGEGEN Alertas"

Capa de red — Netbird VPN mesh (control plane hosteado), 3 peers:
   ├── iot-server  (VM Ubuntu 24.04) ........ grupo: servidores
   ├── Lenovo      (DESKTOP-TROAEG6, Win 11)  grupo: admin
   └── Juana Manso (DESKTOP-ITB975U, Win 10)  grupo: admin
   Política activa: admin → servidores, TCP 1883

Administración: SSH del Lenovo a la VM por NAT + port forwarding (puerto 22) → alias `ssh iot-vm`
```

**Nota clave:** el puente y el bot corren *dentro* de la VM, así que le pegan a InfluxDB y a Mosquitto sin cruzar la red. El único tráfico que viaja por la red Netbird es el de los simuladores Windows hacia el broker. Como Mosquitto escucha **solo** en la IP de Netbird (`100.91.59.9`), nadie se conecta por `localhost` — todos (simuladores y puente) usan esa IP.

### Arquitectura objetivo

```
Generadores en campo (distribuidos en Formosa)
        ↓ sensores físicos
Nodo de campo (SBC o ESP32)
        ↓ preprocesamiento local (*)
        ↓ MQTT sobre red segura (Netbird VPN mesh)
Mosquitto (servidor central)
        ↓
InfluxDB (servidor central)
        ↓
App web propia (visualización y control)
Bot de Telegram (alertas + consultas interactivas)

Capa de red:
  Netbird — VPN mesh, ya operativo
  SDN — gestión programática de la red entre sitios (en evaluación)
```

(*) El preprocesamiento en el nodo de campo reduce el tráfico al servidor y permite detectar eventos críticos localmente, sin depender de conectividad constante. Su ubicación exacta (nodo vs. servidor) se define al definir el hardware de campo.

Los puntos de arquitectura todavía sin cerrar están en la [sección 11](#11-decisiones-abiertas).

---

## 3. Mi rol

**EIyS — Encargada de Infraestructura y Servidor**

Lo que me corresponde:
- Ubuntu Server (VM local por ahora, luego servidor real)
- Mosquitto MQTT broker
- InfluxDB
- Puente MQTT → InfluxDB
- Bot de Telegram (alertas y, a futuro, consultas interactivas)
- Netbird (VPN mesh)
- Simulación de datos (corre en el Lenovo y en la Juana Manso, como clientes externos)
- Stress testing
- Documentación de infraestructura

Lo que **no** me corresponde y no toco:
- Nodos físicos, ESP32, sensores, firmware 
- App web, backend de visualización 

---

## 4. Hardware disponible

| Equipo | Specs | Rol actual |
|--------|-------|------------|
| **Lenovo IdeaPad 3** | Ryzen 7, 16 GB RAM, Windows 11 Home | Corre la VM Ubuntu · peer admin en Netbird · simulador externo |
| **Netbook Juana Manso** | Celeron N4020, 4 GB RAM, Windows 10 | Peer admin en Netbird · segundo simulador externo |
| **VM Ubuntu Server** | 4 GB RAM, 2 CPU, 25 GB · Ubuntu 24.04.4 LTS | Servidor: Mosquitto + InfluxDB + puente + bot |
| **SBCs** (Orange Pi u otros) | A definir | Rol sin decidir — nodos de campo y/o servidor futuro |

**Router del proyecto**: dedicado, operativo. Resuelve el client isolation del WiFi institucional.

**VM Ubuntu Server (`iot-server`)**:
- Corriendo en VirtualBox sobre el Lenovo
- Ubuntu Server 24.04.4 LTS
- Specs: 4 GB RAM, 2 CPU, 25 GB disco
- **Adaptador de red: NAT con port forwarding** (puerto 22 para SSH). La visibilidad en la red mesh la da Netbird (IP `100.91.59.9`), no el adaptador de VirtualBox.
- Controlador gráfico: VBoxVGA (fix para el error vmwgfx)

---

## 5. Credenciales y datos de conexión

> ⚠️ No compartir fuera del equipo. La migración de credenciales a `.env` / gestor de secretos está planificada (ver cronograma, 18/06).

### Mosquitto MQTT (en VM Ubuntu)

| Campo | Valor |
|-------|-------|
| Host (desde los simuladores Windows) | `100.91.59.9` (IP Netbird de la VM) |
| Puerto | `1883` |
| Usuario 1 | `iot_user` |
| Usuario 2 | `esp32_node` |
| Archivo de contraseñas | `/etc/mosquitto/passwd` |
| Config | `/etc/mosquitto/conf.d/sigegen.conf` |

### InfluxDB (en VM Ubuntu)

| Campo | Valor |
|-------|-------|
| URL (operativa, desde la VM) | `http://localhost:8086` |
| URL (por Netbird, p.ej. para la UI desde Windows) | `http://100.91.59.9:8086` |
| Usuario | `admin` |
| Organization | `sigegen` |
| Bucket | `generadores` |
| Token | En `/home/florencia/sigegen/token.txt` |

### Bot de Telegram

| Campo | Valor |
|-------|-------|
| Token | En el script (a migrar a `.env`) — generado con @BotFather |
| Chat ID | Configurado en el script |
| Chat destino | "SIGEGEN Alertas" |

### Simulador (corre en Lenovo y Juana Manso, apuntan a la VM)

| Campo | Valor |
|-------|-------|
| Broker host | `100.91.59.9` (IP Netbird) |
| Puerto | `1883` |
| Usuario | `iot_user` |

---

## 6. Cómo levantar el stack

### En la VM Ubuntu — servicios systemd (arrancan solos al reiniciar)

```bash
# Mosquitto
sudo systemctl status mosquitto
sudo systemctl start mosquitto   # si está detenido

# InfluxDB
sudo systemctl status influxdb
sudo systemctl start influxdb
```

### En la VM Ubuntu — puente y bot (hoy se levantan a mano)

```bash
cd ~/sigegen/scripts
source ~/sigegen-venv/bin/activate

python3 puente.py         # en una terminal
python3 telegram_bot.py   # en otra terminal
```

> ⚠️ A diferencia de Mosquitto e InfluxDB, el puente y el bot corren en **foreground**: si reiniciás la VM, no vuelven solos. Convertirlos en servicios systemd está en pendientes.

### En Windows (Lenovo y/o Juana Manso) — simulador

```powershell
python "C:\Users\...\Desktop\sigegen\simulador.py"
```

### Verificar que todo funciona

```bash
# Desde la VM: ver si llegan mensajes del simulador
mosquitto_sub -h 100.91.59.9 -p 1883 -u iot_user -P "TU_PASS" -t "sigegen/generadores/#" -v

# Logs del broker en tiempo real
sudo journalctl -u mosquitto -f

# Confirmar dónde escucha el broker
ss -tlnp | grep 1883     # debería mostrar 100.91.59.9:1883
```

---

## 7. Configuraciones

### Mosquitto en Ubuntu

Ubicación: `/etc/mosquitto/conf.d/sigegen.conf`

```ini
# Listener: SOLO en la interfaz de Netbird (no expuesto en otras interfaces)
listener 1883 100.91.59.9

# Autenticación
allow_anonymous false
password_file /etc/mosquitto/passwd

# Persistencia
persistence true
persistence_location /var/lib/mosquitto/

# Logs
log_type error
log_type warning
log_type notice
log_type information
connection_messages true
log_timestamp true
```

Comandos de gestión:

```bash
# Crear usuario (-c crea el archivo; sin -c agrega sin sobreescribir)
sudo mosquitto_passwd -c /etc/mosquitto/passwd iot_user
sudo mosquitto_passwd /etc/mosquitto/passwd esp32_node

# Recargar / reiniciar
sudo systemctl reload mosquitto
sudo systemctl restart mosquitto
```

### Firewall Ubuntu (ufw)

```bash
sudo ufw allow 1883/tcp   # MQTT (el listener atado a la IP Netbird ya lo restringe a la mesh)
sudo ufw status
```

> El puerto `8086` ya **no** necesita regla: InfluxDB quedó accesible solo en `localhost`.

### VM Ubuntu — configuración VirtualBox

- **Adaptador de red**: NAT con **port forwarding** (host → VM, puerto 22 para SSH)
- **Controlador gráfico**: VBoxVGA (no VMSVGA — fix para error vmwgfx)
- **RAM**: 4 GB | **CPU**: 2 | **Disco**: 25 GB

---

## 8. Scripts y código

### simulador.py — genera datos de 30 generadores

Corre en el **Lenovo** y en la **Juana Manso**, como clientes externos que publican al broker en la VM por la red Netbird.

```python
import paho.mqtt.client as mqtt
import json, time, random

BROKER = "100.91.59.9"   # IP Netbird de la VM
PORT   = 1883
USER   = "iot_user"
PASS   = "TU_PASSWORD"   # ← completar (no versionar la real)

client = mqtt.Client()
client.username_pw_set(USER, PASS)
client.connect(BROKER, PORT)
client.loop_start()
print("Simulador arrancado — 30 generadores publicando cada 5s")

while True:
    for i in range(1, 31):
        gen_id = f"GEN_{i:02d}"
        payload = {
            "generador_id": gen_id,
            "ubicacion":    f"zona_{(i % 5) + 1}",
            "temperatura":  round(random.uniform(60, 120), 2),
            "rpm":          round(random.uniform(1400, 1600), 2),
            "combustible":  round(random.uniform(10, 100), 2)
        }
        client.publish(f"sigegen/generadores/{gen_id}", json.dumps(payload))
    time.sleep(5)
```

**Datos por generador**: temperatura (60–120 °C), RPM (1400–1600), combustible (10–100 %)
**Ubicación**: `zona_1` a `zona_5` (rotativa por generador)
**Topics**: `sigegen/generadores/GEN_XX`
**Frecuencia**: cada 5 segundos

---

### puente.py — mueve datos de MQTT a InfluxDB

Corre en la **VM**. Usa **escritura por lotes** (junta hasta 500 puntos o espera 1 s antes de mandarlos), más eficiente que una escritura por mensaje.

```python
import paho.mqtt.client as mqtt
import json
from influxdb_client import InfluxDBClient, Point, WriteOptions

BROKER    = "100.91.59.9"   # misma IP Netbird que el broker
MQTT_USER = "iot_user"
MQTT_PASS = "TU_PASSWORD"   # ← completar (no versionar la real)

INFLUX_URL    = "http://localhost:8086"   # InfluxDB en la misma VM
INFLUX_TOKEN  = open("/home/florencia/sigegen/token.txt").read().strip()
INFLUX_ORG    = "sigegen"
INFLUX_BUCKET = "generadores"

influx    = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx.write_api(
    write_options=WriteOptions(batch_size=500, flush_interval=1000)
)

def on_message(client, userdata, msg):
    try:
        data  = json.loads(msg.payload)
        point = (
            Point("generador")
            .tag("generador_id", data["generador_id"])
            .tag("ubicacion",    data["ubicacion"])
            .field("temperatura", data["temperatura"])
            .field("rpm",         data["rpm"])
            .field("combustible", data["combustible"])
        )
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
```

**Modelo en InfluxDB**:
- Measurement: `generador`
- Tags: `generador_id`, `ubicacion`
- Fields: `temperatura`, `rpm`, `combustible`

---

### telegram_bot.py — alertas automáticas (y base para consultas interactivas)

Corre en la **VM**. Consulta InfluxDB cada 60 s, evalúa umbrales, evita repetir la misma alerta y avisa cuando un generador vuelve a la normalidad. Hoy solo **empuja** alertas; las consultas interactivas (comandos tipo `/estado`) están pendientes — la función `consultar_ultimo_valor` ya es la base para eso.

```python
"""
SIGEGEN — Bot de alertas Telegram
=================================
Consulta InfluxDB cada X segundos y manda mensajes a Telegram
cuando algún sensor supera los umbrales configurados.

ANTES DE CORRER:
1. Crear el bot con @BotFather en Telegram → te da TELEGRAM_TOKEN
2. Obtener tu chat ID → mandale cualquier mensaje al bot y visitá:
   https://api.telegram.org/bot<TU_TOKEN>/getUpdates
3. Completar las variables de la sección CONFIGURACIÓN
4. Ajustar UMBRALES según lo que defina el compañero de hardware

Dependencias:
    pip install influxdb-client requests
"""

import time
import requests
from influxdb_client import InfluxDBClient

# ============================================================
# CONFIGURACIÓN — completar con tus datos reales
# ============================================================

# --- InfluxDB ---
INFLUX_URL    = "http://localhost:8086"   # o IP Netbird si corrés remoto
INFLUX_TOKEN  = open("/home/florencia/sigegen/token.txt").read().strip()
INFLUX_ORG    = "sigegen"
INFLUX_BUCKET = "generadores"

# --- Telegram ---
TELEGRAM_TOKEN   = "<TU_TOKEN>"      # ← de @BotFather (no versionar el real)
TELEGRAM_CHAT_ID = "<TU_CHAT_ID>"

# --- Comportamiento ---
INTERVALO_SEGUNDOS = 60      # cada cuánto chequea
REPETIR_ALERTA     = False   # True = avisa cada vez que sigue en crítico
                             # False = avisa solo la primera vez, hasta que se normalice

# ============================================================
# UMBRALES
# ============================================================
# Formato: { "nombre_field": ("condicion", valor_umbral, "descripcion legible") }
# condicion puede ser "mayor" o "menor"

UMBRALES = {
    "temperatura": ("mayor", 100,  "Temperatura crítica"),   # °C
    "combustible": ("menor", 20,   "Combustible bajo"),       # %
    "rpm":         ("mayor", 1580, "RPM fuera de rango"),     # RPM
    # Agregá o quitá fields según lo que mande el ESP32
}

# ============================================================
# FUNCIONES
# ============================================================

def enviar_telegram(mensaje: str):
    """Manda un mensaje de texto al chat configurado."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje,
        "parse_mode": "HTML",
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"[ERROR Telegram] {e}")

def consultar_ultimo_valor(client: InfluxDBClient, field: str) -> dict:
    """
    Devuelve el último valor de un field para cada generador.
    Retorna dict: { "GEN_01": 95.3, "GEN_02": 102.1, ... }
    """
    query = f'''
from(bucket: "{INFLUX_BUCKET}")
  |> range(start: -2m)
  |> filter(fn: (r) => r._measurement == "generador")
  |> filter(fn: (r) => r._field == "{field}")
  |> last()
'''
    resultado = {}
    try:
        tables = client.query_api().query(query, org=INFLUX_ORG)
        for table in tables:
            for record in table.records:
                generador_id = record.values.get("generador_id", "desconocido")
                resultado[generador_id] = record.get_value()
    except Exception as e:
        print(f"[ERROR InfluxDB] consultando '{field}': {e}")
    return resultado

def evaluar_umbral(valor, condicion: str, limite) -> bool:
    """Devuelve True si el valor supera el umbral."""
    if condicion == "mayor":
        return valor > limite
    elif condicion == "menor":
        return valor < limite
    return False

def formatear_alerta(generador_id, field, valor, descripcion, condicion, limite) -> str:
    simbolo = "🔴" if condicion == "mayor" else "🟡"
    return (
        f"{simbolo} <b>ALERTA SIGEGEN</b>\n"
        f"Generador: <code>{generador_id}</code>\n"
        f"Sensor: {field}\n"
        f"Estado: {descripcion}\n"
        f"Valor actual: <b>{valor:.1f}</b> (umbral: {condicion} {limite})"
    )

# ============================================================
# LOOP PRINCIPAL
# ============================================================

def main():
    print("=== SIGEGEN Bot de alertas Telegram ===")
    print(f"Chequeando cada {INTERVALO_SEGUNDOS} segundos...")
    print(f"Umbrales activos: {list(UMBRALES.keys())}")
    print("Presioná Ctrl+C para detener.\n")

    # Memoria para no repetir alertas del mismo generador+field
    alertas_activas = set()   # conjunto de (generador_id, field)

    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)

    enviar_telegram("✅ <b>SIGEGEN Bot iniciado</b>\nMonitoreo de generadores activo.")

    try:
        while True:
            alertas_esta_ronda = set()

            for field, (condicion, limite, descripcion) in UMBRALES.items():
                valores = consultar_ultimo_valor(client, field)

                for generador_id, valor in valores.items():
                    clave = (generador_id, field)

                    if evaluar_umbral(valor, condicion, limite):
                        alertas_esta_ronda.add(clave)
                        # Mandar alerta si no estaba activa, o si se repite siempre
                        if clave not in alertas_activas or REPETIR_ALERTA:
                            msg = formatear_alerta(generador_id, field, valor, descripcion, condicion, limite)
                            enviar_telegram(msg)
                            print(f"[ALERTA] {generador_id} — {field}: {valor:.1f}")
                    else:
                        # Si estaba en alerta y ahora se normalizó, avisar
                        if clave in alertas_activas:
                            enviar_telegram(
                                f"✅ <b>Normalizado</b>\n"
                                f"Generador: <code>{generador_id}</code>\n"
                                f"Sensor {field} volvió a valores normales ({valor:.1f})"
                            )
                            print(f"[OK] {generador_id} — {field} normalizado: {valor:.1f}")

            alertas_activas = alertas_esta_ronda
            time.sleep(INTERVALO_SEGUNDOS)

    except KeyboardInterrupt:
        print("\nBot detenido.")
        enviar_telegram("⚠️ <b>SIGEGEN Bot detenido</b>")
        client.close()

if __name__ == "__main__":
    main()
```

**Umbrales activos**: temperatura > 100 °C · combustible < 20 % · RPM > 1580
**Chequeo**: cada 60 s · **Destino**: chat "SIGEGEN Alertas"

---

### Comandos útiles de prueba rápida

```bash
# Ver mensajes que llegan al broker (desde la VM)
mosquitto_sub -h 100.91.59.9 -p 1883 -u iot_user -P "TU_PASS" -t "sigegen/generadores/#" -v

# Publicar mensaje de prueba manual
mosquitto_pub -h 100.91.59.9 -p 1883 -u iot_user -P "TU_PASS" -t "sigegen/test" -m "hola"

# Logs del broker en tiempo real
sudo journalctl -u mosquitto -f

# Ver qué puertos están escuchando
ss -tlnp
```

---

## 9. Errores conocidos y soluciones

### ❌ Verificación de paquete InfluxData falla por rotación de subclave GPG (enero 2026)

**Síntoma**: la verificación por hash SHA del paquete/repositorio de InfluxData fallaba.
**Causa**: InfluxData rotó su subclave de firma; el SHA dejó de coincidir.
**Solución**: verificar el **fingerprint primario** de la clave GPG en lugar del hash del archivo.

---

### ❌ Servicio Mosquitto Windows no arrancaba con config personalizada

**Síntoma**: el servicio se detenía solo al iniciar.
**Causa**: el `binPath` no incluía el flag `-c` apuntando al config.
**Estado**: ya no aplica — ahora corre en Ubuntu como servicio systemd.

---

### ❌ Multipass no importaba imágenes Ubuntu en Windows 11 Home

**Causa**: bug con backend VirtualBox en Windows 11 Home.
**Solución**: descartado. Se usa VirtualBox directamente.

---

### ❌ Oracle Cloud Free Tier — registro rechazado

**Síntoma**: verificación de identidad falla.
**Estado**: **descartado** como opción de servidor. Plan B: Hetzner CX22 (~€4/mes) o SBC físico.

---

### ❌ Instalación Ubuntu en VM — loop de descarga de linux-firmware (641 MB)

**Síntoma**: el instalador reintentaba descargas que el WiFi institucional cortaba.
**Solución**:
1. Adaptador de red → NAT
2. Al llegar a "Configure Ubuntu archive mirror" → desconectar red de la VM
3. La instalación termina con paquetes del ISO
4. Reiniciar → reactivar red → `sudo apt update && sudo apt upgrade -y`

---

### ❌ Client isolation en WiFi institucional

**Causa**: medida de seguridad estándar en redes educativas.
**Solución**: router dedicado del proyecto.

---

### ❌ Error vmwgfx al iniciar VM en VirtualBox

**Causa**: controlador gráfico VMSVGA incompatible.
**Solución**: Configuración → Pantalla → Controlador gráfico → **VBoxVGA**.

---

### ⚠️ DeprecationWarning de `mqtt.Client()` (baja prioridad)

**Síntoma**: warning "Callback API version 1 is deprecated" al arrancar los scripts.
**Causa**: paho-mqtt 2.x deprecó la API de callbacks v1.
**Estado**: inofensivo. Se resuelve pasando a la nueva Callback API cuando convenga.

---

### Diagnóstico rápido de conexión MQTT

| Mensaje | Causa probable | Qué revisar |
|---------|---------------|-------------|
| `Connection refused` | Broker no corre o IP equivocada | ¿`systemctl status mosquitto`? ¿IP `100.91.59.9`? |
| `Connection timed out` | Peer fuera de la mesh o sin política | ¿Peer conectado en Netbird? ¿Política admin→servidores? |
| `Not authorized` | Credenciales incorrectas | Mayúsculas, espacios, contraseña exacta |

---

## 10. Decisiones tomadas y por qué

| Decisión | Alternativa descartada | Razón |
|----------|----------------------|-------|
| MQTT como protocolo | HTTP / WebSockets | Pensado para IoT: liviano, tolera conexiones inestables, pub/sub nativo |
| Mosquitto como broker | RabbitMQ, EMQX | Liviano, bien documentado, referencia en IoT de escala similar |
| InfluxDB como base de datos | PostgreSQL, MongoDB | Serie de tiempo: optimizada para datos con timestamp de sensores |
| InfluxDB con Flux | InfluxQL | InfluxDB 2.x usa Flux como lenguaje principal; InfluxQL es de v1.x |
| Escritura por lotes en el puente | Escritura sincrónica | Mejor throughput con 30 generadores cada 5 s |
| Ubuntu Server como SO | Windows Server | Entorno estándar del stack; systemd gestiona los servicios |
| Lenovo como cliente simulador | Simular desde la propia VM | Reproduce el escenario real: nodo externo publicando al servidor |
| Router dedicado del proyecto | WiFi institucional | El client isolation impedía la comunicación entre equipos |
| Mosquitto escuchando en IP Netbird | Escuchar en `0.0.0.0` | El broker solo acepta conexiones por la mesh; el puerto no queda expuesto |
| Netbird como VPN mesh (managed) | OpenVPN, WireGuard manual | Zero Trust: los nodos se conectan sin exponer el servidor |
| Mosquitto con auth (`allow_anonymous false`) | Sin autenticación | Requisito básico de seguridad con datos operativos reales |
| App web propia (futura) | Grafana | Interfaz específica para generadores heterogéneos; Grafana es genérica |
| Telegram como canal (alertas + consultas interactivas) | Email, SMS, dashboard propio | API simple, sin infra extra, accesible desde el celular |

---

## 11. Decisiones abiertas

| Tema | Opciones | Estado |
|------|----------|--------|
| **SBCs** | Nodos de campo / servidor / ambos | ❓ Sin decidir |
| **Preprocesamiento** | En nodo de campo o en servidor central | ❓ Sin decidir |
| **SDN-WAN** | Incluir si se justifica para la distribución geográfica | ❓ En evaluación |
| **Servidor final** | Hetzner / SBC físico / VM local permanente | ❓ Oracle descartado |
| **Alcance del sistema** | Solo monitoreo / monitoreo + control de generadores | ❓ Por definir con el equipo |
| **Netbird self-host** | Managed (actual) / self-hosted a futuro | 🟡 Managed por ahora; self-host como opción futura |

> Cerrado recientemente: **alcance del bot** → alertas + consultas interactivas (las consultas, pendientes de implementar).

---

## 12. Pendientes y próximos pasos

### Entrega parcial — 25 junio 2026

Foco: stack de infraestructura funcionando y demostrable.

- [x] Mosquitto en Ubuntu — recibe datos del simulador
- [x] InfluxDB en Ubuntu — almacena correctamente
- [x] Simulador corriendo en el Lenovo (y en la Juana Manso) publicando a la VM
- [x] Puente funcionando (MQTT → InfluxDB)
- [x] Netbird: peers conectados (3) + grupos + política Zero Trust
- [~] Documentación básica de infraestructura (en curso)

**De yapa, ya hecho (no estaba en el checklist mínimo):** bot de alertas por Telegram, segundo simulador externo, políticas Zero Trust y escritura por lotes.

### Después de la parcial → entrega final (octubre)

- [ ] Definir el rol de los SBCs e integrarlos
- [ ] Definir y ubicar el preprocesamiento (nodo vs. servidor)
- [ ] Resolver el servidor final (Hetzner / SBC / VM local permanente)
- [ ] Evaluar e integrar SDN-WAN si se justifica
- [ ] Convertir el puente y el bot en servicios systemd
- [ ] Implementar las consultas interactivas del bot (comandos tipo `/estado`)
- [ ] Stress test: múltiples nodos concurrentes
- [ ] Medir latencia end-to-end
- [ ] Prueba de campo con nodo real (48 hs)
- [ ] Integración final con el track de hardware (ESP32)
- [ ] Sesión de seguridad: migrar credenciales a `.env` / gestor, rotación de tokens (cronograma 18/06)
- [ ] Documentación final: README, diagramas, manual

---

## 13. Glosario rápido

**MQTT** — Protocolo de mensajería liviano para IoT. Publicadores envían datos a un broker; suscriptores los reciben. Ideal para conexiones inestables y dispositivos con recursos limitados.

**Broker** — El "distribuidor" de MQTT. Recibe mensajes y los entrega según el topic.

**Topic** — La "dirección" de un mensaje MQTT. Ejemplo: `sigegen/generadores/GEN_01`. `#` es comodín multinivel; `+` es de un solo nivel.

**InfluxDB** — Base de datos de series de tiempo. Guarda datos con timestamp, ideal para sensores.

**Flux** — Lenguaje de consulta de InfluxDB 2.x. Distinto de SQL o InfluxQL (que es de v1.x).

**Escritura por lotes (batch writes)** — En vez de escribir cada punto al instante, se acumulan varios (hasta `batch_size`) o se espera un tiempo (`flush_interval`) y se mandan juntos. Reduce el costo por escritura.

**App web propia** — Interfaz visual de desarrollo propio que reemplaza a Grafana. Muestra el estado de los generadores en tiempo real. 

**Netbird** — VPN mesh Zero Trust. Conecta nodos de forma segura sin servidor de paso central. Permite definir políticas de acceso por grupo y protocolo.

**Zero Trust** — Modelo de seguridad donde ningún nodo tiene acceso por defecto: cada conexión se valida contra políticas definidas. Netbird implementa este modelo.

**SDN (Software Defined Networking)** — Arquitectura donde el plano de control (quién decide cómo van los paquetes) está separado del plano de datos (quién los mueve). El controlador opera en capa 3. Permite programar el comportamiento de la red por software.

**SDN-WAN** — Variante de SDN para redes de área amplia (entre sitios geográficos distantes). Relevante para SIGEGEN si se justifica: los generadores están distribuidos en distintos puntos de Formosa.

**SBC (Single Board Computer)** — Computadora de placa única (Orange Pi, Raspberry Pi, etc.). Posibles usos: nodos de campo o servidor central. Rol sin decidir.

**Preprocesamiento** — Procesamiento de datos antes de que lleguen al servidor central. Puede hacerse en el nodo de campo (reduce tráfico, detecta eventos localmente) o en el servidor. Ubicación sin decidir.

**Puente** — Script Python que suscribe al broker MQTT y escribe los datos recibidos en InfluxDB.

**Bot de Telegram** — Componente de notificación. Hoy manda alertas automáticas cuando un generador supera umbrales; a futuro, también responderá consultas interactivas de estado.

**Foreground** — Proceso que corre en una terminal abierta: si cerrás la terminal, muere. Los servicios systemd, en cambio, corren como daemons en segundo plano.

**systemd** — Sistema de init de Ubuntu. Gestiona servicios: `systemctl start/stop/status/enable`. Con `enable`, el servicio arranca solo al reiniciar la VM.

**NAT + port forwarding** — La VM usa una red NAT (privada) de VirtualBox; el port forwarding expone un puerto del host hacia la VM (acá, el 22 para SSH). La conectividad de la mesh la da Netbird, no el adaptador.

**Generadores heterogéneos** — Generadores de distintos modelos, marcas y capacidades. El sistema tiene que manejar distintos tipos de sensores y protocolos.
