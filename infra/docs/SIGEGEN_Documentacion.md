# Documentación SIGEGEN — Refactorizada y consolidada

> Tres documentos en uno: README (operativo), ARQUITECTURA (conceptual), WIKI (referencia).
> Sin duplicación, sin roles, trabajo colaborativo.

---

# ÍNDICE

- [README](#readme) — Cómo levantar y operar el sistema
- [ARQUITECTURA](#arquitectura) — Decisiones, por qué, puntos abiertos
- [WIKI](#wiki) — Referencia, glosario, estado actual

---

---

# README

## 1. Qué es SIGEGEN

Sistema de monitoreo de generadores heterogéneos distribuidos en Formosa. El equipo desarrolla un stack que:

1. Recibe datos de sensores (temperatura, RPM, combustible, etc.)
2. Los almacena en tiempo real
3. Genera alertas automáticas
4. Visualiza el estado en un dashboard

El flujo de datos:

```
Sensores (ESP32)  →  MQTT Broker  →  Puente Python  →  InfluxDB
                                                          ↓
                                                   Bot Telegram (alertas)
                                                   Dashboard web (visualización)
```

Todos los componentes están conectados por **Netbird**, una VPN mesh que crea una red segura sin exponer nada a internet.

---

## 2. Requisitos mínimos

| Componente | Especificación |
|------------|---|
| **VM Servidor** | Ubuntu Server 24.04.4 LTS — 4 GB RAM, 2 CPU, 25 GB disco |
| **Virtualización** | VirtualBox con adaptador NAT · Controlador gráfico VBoxVGA |
| **Python** | 3.12.3 |
| **Mosquitto** | 2.0.18 |
| **InfluxDB** | 2.9.1 |
| **Librerías Python** | paho-mqtt 2.1.0 · influxdb-client 1.50.0 |
| **Red** | Netbird instalado, servidor registrado como peer en grupo `servidores` |
| **Acceso** | SSH con alias configurado (ej: `ssh iot-vm`) |

---

## 3. Los servicios principales

Cuatro procesos corren como servicios **systemd** (arrancan solos al bootear):

| Servicio | Función | Escucha/Escribe |
|----------|---------|-----------------|
| `mosquitto` | Broker MQTT (coordina publicadores y suscriptores) | `100.91.59.9:1883` (IP Netbird) |
| `influxdb` | Base de datos de series de tiempo | `localhost:8086`, bucket `generadores` |
| `iot-puente` | Lee MQTT, escribe en InfluxDB por lotes | Topic `sigegen/generadores/#` → InfluxDB |
| `iot-bot` | Consulta InfluxDB cada 60s, dispara alertas | InfluxDB → chat Telegram |

Scripts: `~/sigegen/scripts/` · Entorno Python 3.12.3: `~/sigegen-venv/`

---

## 4. Levantar el sistema

### Encender

```bash
# 1. Arrancar VM en VirtualBox, esperar a que bootee

# 2. Conectarse por SSH
ssh iot-vm

# 3. Verificar que los servicios están activos
systemctl is-active mosquitto influxdb iot-puente iot-bot
# Respuesta esperada: active (4 veces)

# Si alguno no está active, revisar logs:
sudo systemctl status <servicio>
sudo journalctl -u <servicio> -n 50
```

### Publicar datos (simuladores en Windows)

```powershell
# Desde el Lenovo o Juana Manso
python "C:\ruta\a\simulador.py"
# Publica 30 generadores, 1 msg cada 5 segundos
```

### Verificar el flujo

```bash
# 1. Ver mensajes en vivo en el broker
mosquitto_sub -h 100.91.59.9 -p 1883 -u iot_user -P "contraseña" \
  -t "sigegen/generadores/#" -v

# 2. Confirmar broker escuchando
ss -tlnp | grep 1883
# Debe mostrar: 100.91.59.9:1883 LISTEN

# 3. Ver datos escritos en InfluxDB
sudo journalctl -u iot-puente -f
# Debe mostrar: escribe puntos en el bucket

# 4. Ver alertas (si hay)
sudo journalctl -u iot-bot -f
```

### Apagar

```bash
sudo poweroff
# Los servicios systemd se detienen ordenadamente
```

---

## 5. Resolución de problemas

### Patrón general

```bash
sudo systemctl status <servicio>          # estado + últimas líneas
sudo journalctl -u <servicio> -e          # log completo (final)
sudo systemctl restart <servicio>         # reiniciar
```

### Mosquitto no conecta o no arranca

**Síntoma:** "Connection refused" o `systemctl status mosquitto` muestra `failed`

**Diagnóstico:**
```bash
sudo journalctl -u mosquitto -e
```

Buscar:
- `Cannot assign requested address` → problema de arranque (IP Netbird no existe aún). **Solución:** revisar que `net.ipv4.ip_nonlocal_bind = 1` en `/etc/sysctl.d/99-nonlocal-bind.conf` (ver sección 6)
- Error en config → revisar `/etc/mosquitto/conf.d/sigegen.conf`
- Puerto ocupado → `ss -tlnp | grep 1883`

**Solución:** `sudo systemctl restart mosquitto`

### InfluxDB no escribe

**Síntoma:** Puente loguea errores, datos no aparecen en InfluxDB

**Diagnóstico:**
```bash
sudo systemctl status influxdb
sudo journalctl -u influxdb -e
```

**Solución:** `sudo systemctl restart influxdb`

### Puente caído (datos en MQTT pero no en InfluxDB)

**Diagnóstico:**
```bash
sudo systemctl status iot-puente
sudo journalctl -u iot-puente -e
```

Buscar: token vencido, InfluxDB caído, credenciales MQTT incorrectas

**Solución:** `sudo systemctl restart iot-puente`

### Bot no envía alertas

**Diagnóstico:**
```bash
sudo systemctl status iot-bot
sudo journalctl -u iot-bot -e
```

Buscar: token Telegram inválido, InfluxDB sin acceso

**Solución:** `sudo systemctl restart iot-bot`

### Cliente (simulador) no conecta a Mosquitto

| Mensaje | Causa | Solución |
|---------|-------|----------|
| `Connection refused` | Broker no corre o IP incorrecta | Verificar `systemctl status mosquitto` y IP (`100.91.59.9`) |
| `Connection timed out` | Sin ruta a Netbird o fuera de la malla | Verificar `netbird status` en cliente, `ping 100.91.59.9` |
| `Not authorized` | Credenciales incorrectas | Verificar usuario/contraseña exactos (mayúsculas, espacios) |

### Cliente Netbird no conecta

```bash
# Desde Windows
netbird status
```

| Estado | Significado | Acción |
|--------|-------------|--------|
| `Connected` | Red OK | Problema es MQTT, ver tabla anterior |
| `NeedsLogin` | SSO expiró (24h) | `netbird up` (reautenticar en navegador) |
| Daemon no responde | Servicio caído | Reiniciar servicio Netbird |

---

## 6. El arreglo crítico: Mosquitto y Netbird al boot

**Problema:** Mosquitto intenta atarse a la IP de Netbird (`100.91.59.9`) antes de que Netbird la asigne, fallando con `Cannot assign requested address`.

**Solución aplicada:**
```bash
# Archivo: /etc/sysctl.d/99-nonlocal-bind.conf
net.ipv4.ip_nonlocal_bind = 1
```

Permite que un proceso se ate a una IP que no existe *aún*. Aplicado con `sudo sysctl --system`.

**Verificar:**
```bash
sysctl net.ipv4.ip_nonlocal_bind
# Debe retornar: net.ipv4.ip_nonlocal_bind = 1
```

Si Mosquitto vuelve a fallar al boot, lo primero a revisar es que este valor siga en `1`.

---

## 7. Datos de conexión

| Recurso | Valor |
|---------|-------|
| SSH servidor | `ssh iot-vm` |
| Broker MQTT | `100.91.59.9:1883` |
| Usuarios MQTT | `iot_user`, `esp32_node` |
| Config Mosquitto | `/etc/mosquitto/conf.d/sigegen.conf` |
| Contraseñas MQTT | `/etc/mosquitto/passwd` |
| InfluxDB | `http://localhost:8086` |
| Org/Bucket | `sigegen` / `generadores` |
| Token InfluxDB | `~/sigegen/token.txt` |
| Scripts | `~/sigegen/scripts/` |
| Venv Python | `~/sigegen-venv/` |

⚠️ **Credenciales:** Nunca en repositorio. Usar `.env` o gestor de secretos.

---

---

# ARQUITECTURA

## 1. Decisiones fundamentales

### MQTT como protocolo

**Por qué:** Diseñado para IoT. Liviano, tolerante a conexiones inestables, pub/sub nativo.

**Alternativas descartadas:** HTTP (más overhead), WebSockets (menos maduro para IoT).

### Mosquitto como broker

**Por qué:** Referencia en proyectos IoT de escala similar, bien documentado, bajo consumo de recursos.

**Alternativas descartadas:** RabbitMQ (más pesado), EMQX (más complejo).

### InfluxDB como base de datos

**Por qué:** Optimizada para series de tiempo (datos con timestamp). Ideal para sensores.

**Alternativas descartadas:** PostgreSQL (no especializada en time-series), MongoDB (no es TSDB).

### Netbird como VPN mesh

**Por qué:** Zero Trust architecture. Los nodos se conectan sin exponer el servidor a internet.

**Alternativas descartadas:** OpenVPN (requiere central), WireGuard manual (requiere más configuración).

### Autenticación en Mosquitto

**Por qué:** Requisito de seguridad. Los datos son operativos, no pueden fluir anónimamente.

---

## 2. Flujo de datos

```
Sensor/ESP32
  ↓ JSON con temp, RPM, combustible
Nodo de campo (o simulador)
  ↓ MQTT topic: sigegen/generadores/GEN_XX (QoS 1)
Mosquitto Broker
  ↓ suscripción: sigegen/generadores/#
Puente Python
  ↓ parsea JSON, construye punto InfluxDB
InfluxDB (measurement: generador, tags: ID/ubicación, fields: temp/RPM/combustible)
  ↓ consulta Flux cada 60s
Bot Telegram
  ↓ umbral superado → alerta al chat
Dashboard web (futuro)
  ↓ visualización en tiempo real
Equipo
```

---

## 3. Capa de red: Netbird + SDN

**Netbird:** conecta todos los peers (Lenovo, Juana Manso, servidor, nodos de campo) en una malla privada. El broker solo escucha en la IP de Netbird.

**SDN (en evaluación):** para distribución geográfica entre generadores en Formosa. Permite programar las rutas de datos por software en vez de por hardware.

---

## 4. Decisiones abiertas

| Tema | Opciones | Estado |
|------|----------|--------|
| **SBCs** | ¿Nodos de campo, servidor, o ambos? | Sin decidir |
| **Preprocesamiento** | ¿En nodo de campo (reduce tráfico) o en servidor (centraliza lógica)? | Sin decidir |
| **Bot de Telegram** | ¿Solo alertas pasivas o también consultas interactivas? | Sin definir |
| **Alcance** | ¿Solo monitoreo o también control activo de generadores? | Por definir |
| **Servidor final** | ¿VM local, cloud (Hetzner), o SBC físico? | En evaluación |

---

## 5. Supuestos y restricciones

- **Latencia aceptable:** < 1 segundo para alertas (sensible a cómo se distribuya)
- **Throughput:** escalable a 100+ generadores simultáneos (depende de tuning Mosquitto, InfluxDB)
- **Disponibilidad:** sin redundancia en lab, pero el stack es tolerante a reconexiones
- **Seguridad:** Netbird Zero Trust cubre la malla; credenciales en `.env` (no en repo)

---

---

# WIKI

## 1. Estado actual del proyecto

| Componente | Estado | Notas |
|-----------|--------|-------|
| **Mosquitto** | ✓ Operativo | Auth, escucha en IP Netbird, persistencia activada |
| **InfluxDB** | ✓ Operativo | Bucket `generadores` creado, retention 30 días |
| **Puente MQTT→InfluxDB** | ✓ Operativo | Escribe por lotes, maneja errores |
| **Bot Telegram** | ✓ Operativo | Umbrales: temp > 100°C, combustible < 20%, RPM > 1580 |
| **Simulador** | ✓ Funcional | 30 generadores, intervalo 5s, formato JSON |
| **Netbird** | ✓ Operativo | 3+ peers conectados, políticas Zero Trust activas |
| **Dashboard web** | ⏳ Pendiente | Para octubre |
| **SDN integración** | ⏳ En evaluación | Después de parcial |

---

## 2. Estructura del repositorio

```
sigegen/
├── README.md                          ← este documento (operativo)
├── ARQUITECTURA.md                    ← decisiones y por qué
├── WIKI.md                            ← referencia (este)
├── infra/
│   ├── README_infraestructura.md
│   ├── .gitignore
│   ├── config/
│   │   └── mosquitto.conf.txt
│   ├── docs/
│   │   ├── 00_wiki_sigegen.md
│   │   ├── cronograma_iot.md
│   │   └── arquitectura_sigegen_v2.pdf
│   └── scripts/
│       ├── simulador.py
│       ├── puente.py
│       ├── telegram_bot.py
│       ├── latency_probe.py
│       ├── stress_publish.py
│       └── backup.sh
├── hardware/                          ← pista hardware (a organizar)
└── software/                          ← pista software (a organizar)
```

---

## 3. Cronograma (fases lógicas, sin fechas rígidas)

### Fase 1 — Educación mutua
Cada quien enseña lo que sabe. El equipo entiende la arquitectura completa.

### Fase 2 — Stack básico funcionando
Mosquitto + InfluxDB + Puente + Bot en laboratorio.

### Fase 3 — Nodo real (no simulado)
Integración del generador real. 48 hs de operación.

### Fase 4 — Ataque al sistema (stress test)
10 tipos de ataque: volumen, tamaño, volatilidad, malformación, desconexiones, latencia, seguridad, falla de componentes, recuperación, carga desigual.

### Fase 5 — Hardening y seguridad
Backups, recuperación automática, credenciales seguras.

### Fase 6 — Documentación final
README, runbooks, manual de operación.

---

## 4. Modelo de datos en InfluxDB

```
Measurement: generador

Tags (indexados, para filtrado):
  - generador_id (ej: GEN_01)
  - ubicacion (ej: zona_1)

Fields (valores numéricos):
  - temperatura (°C)
  - rpm (revoluciones/min)
  - combustible (%)

Timestamp: auto (momento en que se escribió)
```

Ejemplo de punto:
```
generador,generador_id=GEN_01,ubicacion=zona_1 temperatura=87.3,rpm=1520.5,combustible=75.2 1718000000000000000
```

---

## 5. Topics MQTT

```
sigegen/generadores/GEN_XX
```

Cada mensaje es JSON:
```json
{
  "generador_id": "GEN_01",
  "ubicacion": "zona_1",
  "temperatura": 87.3,
  "rpm": 1520.5,
  "combustible": 75.2
}
```

QoS 1 (garantiza al menos una entrega).

---

## 6. Credenciales (gestión)

| Secreto | Ubicación actual | Ubicación ideal |
|---------|-----------------|-----------------|
| Token InfluxDB | `~/sigegen/token.txt` | `.env` |
| Contraseñas Mosquitto | `/etc/mosquitto/passwd` | `.env` o gestor |
| Token Bot Telegram | hardcoded en script | `.env` |
| Netbird setup key | en servidor | `.env` |

**Plan:** migrar todo a `.env` después de la parcial.

---

## 7. Glosario

**MQTT** — Protocolo de mensajería pub/sub para IoT. Publicadores envían a topics, suscriptores reciben.

**Broker** — El coordinador MQTT. Recibe mensajes y los distribuye según topic.

**QoS** — Quality of Service en MQTT. 0 (máximo una), 1 (al menos una), 2 (exactamente una).

**Topic** — Dirección jerárquica en MQTT. `sigegen/generadores/GEN_01` con comodines `+` (un nivel) y `#` (todo lo que sigue).

**InfluxDB** — Base de datos de series de tiempo. Almacena (timestamp, tags, fields).

**Flux** — Lenguaje de consulta de InfluxDB 2.x (distinto a InfluxQL v1.x).

**Netbird** — VPN mesh Zero Trust. Los peers se conectan peer-to-peer sin servidor central.

**Zero Trust** — Modelo de seguridad: ningún peer tiene acceso por defecto, cada conexión se valida contra políticas.

**Systemd** — Gestor de servicios de Ubuntu. `systemctl start/stop/status/restart`.

**Setup key** — Credencial para registrar un peer en Netbird sin login SSO (útil para servidores).

**Puente** — Script que lee MQTT y escribe en InfluxDB (transformación de datos).

**Stress test** — Prueba de capacidad. ¿Cuántos msg/s aguanta? ¿A qué latencia? ¿Dónde se quiebra?

**Latencia P50, P95, P99** — Percentiles de latencia. P50 es la mediana, P99 es los muy lentos.

**Retention policy** — Cuánto tiempo InfluxDB guarda datos antes de borrar.

---

## 8. Contactos y permisos

- **Repositorio:** `github.com/iamDiecan/Proyecto-Final-Sistema-Monitoreo-...`
- **Colaboradores:** [nombres de equipo — agregarlos]
- **Issues/PRs:** usar etiquetas `infra`, `hardware`, `software`, `docs` para organizar

---

## 9. Próximos pasos (post-parcial)

- [ ] Definir rol de SBCs (nodo vs servidor vs ambos)
- [ ] Decidir ubicación del preprocesamiento
- [ ] Resolver servidor final (cloud vs SBC)
- [ ] Implementar SDN-WAN para distribución en Formosa
- [ ] Iniciar desarrollo de dashboard web
- [ ] Definir alcance del control (solo monitoreo o comando)
- [ ] Migrar secretos a `.env` / gestor

---

**Última actualización:** junio 2026 (refactorización colaborativa)
