# README — Infraestructura SIGEGEN 

> Cómo levantar el stack de cero, operarlo día a día y qué hacer si algo se cae.
> Para el "por qué" de cada decisión (MQTT vs HTTP, Mosquitto, InfluxDB, Netbird), ver el documento de arquitectura.

---

## 1. Qué es

El servidor de SIGEGEN recibe datos de generadores (hoy simulados), los almacena y dispara alertas. El flujo es:

```
Simuladores (Windows)  →  Mosquitto (MQTT)  →  puente  →  InfluxDB
                                                              ↓
                                                    bot de Telegram (alertas)
```

Toda la comunicación pasa por la red segura **Netbird**: el broker no está expuesto a internet, solo es accesible desde la malla.

---

## 2. Requisitos

| Componente | Detalle |
|------------|---------|
| VM | Ubuntu Server 24.04.4 LTS — 4 GB RAM, 2 CPU, 25 GB disco |
| VirtualBox | Adaptador **NAT con port forwarding** (host→VM puerto 22 para SSH) · Controlador gráfico **VBoxVGA** |
| Red | Netbird instalado, VM como peer `iot-server` en el grupo `servidores` |
| Paquetes | `mosquitto`, `mosquitto-clients`, InfluxDB 2.x, entorno Python (`paho-mqtt`, `influxdb-client`) |
| Acceso | SSH con alias: `ssh iot-vm` |

---

## 3. Los cuatro servicios

Todos corren como servicios **systemd** y están habilitados (`enabled`): **arrancan solos al reiniciar la VM**.

| Servicio systemd | Qué hace | Escucha / escribe |
|------------------|----------|-------------------|
| `mosquitto` | Broker MQTT con autenticación | Escucha en `100.91.59.9:1883` (solo IP Netbird) |
| `influxdb` | Base de datos de series de tiempo | `localhost:8086`, bucket `generadores` |
| `iot-puente` | Suscribe al broker y escribe en InfluxDB (por lotes) | Topic `sigegen/generadores/#` → InfluxDB |
| `iot-bot` | Consulta InfluxDB cada 60 s y manda alertas | InfluxDB → chat "SIGEGEN Alertas" |

Scripts del puente y el bot: `~/sigegen/scripts/` · entorno virtual: `~/sigegen-venv/`.

---

## 4. Levantar todo de cero / operación normal

### Encender

1. Iniciar la VM en VirtualBox y esperar a que termine de bootear.
2. Entrar por SSH:
   ```bash
   ssh iot-vm
   ```
3. **No hay que arrancar nada a mano.** Los cuatro servicios levantan solos. Verificar:
   ```bash
   systemctl is-active mosquitto influxdb iot-puente iot-bot
   ```
   Deberían responder `active` los cuatro. Para ver el detalle de uno:
   ```bash
   sudo systemctl status mosquitto
   ```

### Arrancar los simuladores (Windows — Lenovo y/o Juana Manso)

```powershell
python "C:\Users\...\Desktop\sigegen\simulador.py"
```

Publican 30 generadores (`GEN_01`…`GEN_30`) cada 5 s al broker por Netbird.

### Verificar que el dato fluye

```bash
# Ver mensajes llegando al broker en vivo
mosquitto_sub -h 100.91.59.9 -p 1883 -u iot_user -P "TU_PASS" -t "sigegen/generadores/#" -v

# Confirmar dónde escucha el broker (debe ser 100.91.59.9:1883)
ss -tlnp | grep 1883

# Ver el puente escribiendo en InfluxDB
sudo journalctl -u iot-puente -f
```

### Apagar

```bash
sudo poweroff
```

Esto detiene los cuatro servicios de forma ordenada. No hay nada que "guardar" antes de apagar.

---

## 5. El arreglo del arranque de Mosquitto (importante)

Mosquitto está configurado para escuchar **solo** en la IP de Netbird (`100.91.59.9`). El problema: al bootear, esa IP todavía no existe (Netbird tarda unos segundos en asignarla), así que Mosquitto intentaba atarse a una dirección inexistente y fallaba con `Cannot assign requested address`, dándose por vencido.

**La solución** (ya aplicada) permite que un proceso se ate a una IP que todavía no existe:

```
# Archivo: /etc/sysctl.d/99-nonlocal-bind.conf
net.ipv4.ip_nonlocal_bind = 1
```

Aplicado con `sudo sysctl --system`. Verificable con:

```bash
sysctl net.ipv4.ip_nonlocal_bind    # debe devolver = 1
```

Si algún día Mosquitto vuelve a fallar al boot con ese error, lo primero a revisar es que este valor siga en `1`.

---

## 6. Runbook — qué hacer si se cae un componente

Patrón general para cualquiera de los cuatro servicios:

```bash
sudo systemctl status <servicio>      # ver estado y últimas líneas
sudo journalctl -u <servicio> -e      # ver el log completo (final)
sudo systemctl restart <servicio>     # reiniciar
```

### Mosquitto caído

- **Síntoma:** los simuladores no conectan; `systemctl status mosquitto` muestra `failed`.
- **Diagnóstico:** `sudo journalctl -u mosquitto -e`.
  - Si dice `Cannot assign requested address` → es el problema de arranque: revisar `nonlocal_bind` (sección 5) y que Netbird esté arriba (`ip a | grep 100.91`).
  - Si dice error en la config → revisar `/etc/mosquitto/conf.d/sigegen.conf`.
- **Solución:** corregido el problema, `sudo systemctl restart mosquitto`.

### InfluxDB caído

- **Síntoma:** el puente loguea errores de escritura; el bot no encuentra datos.
- **Diagnóstico:** `sudo systemctl status influxdb` y `sudo journalctl -u influxdb -e`.
- **Solución:** `sudo systemctl restart influxdb`. Verificar que vuelve a escuchar en `localhost:8086`.

### Puente caído

- **Síntoma:** llegan mensajes al broker (`mosquitto_sub` los ve) pero no aparecen en InfluxDB.
- **Diagnóstico:** `sudo systemctl status iot-puente`. Como tiene `Restart=on-failure`, si crasheó debería haber vuelto solo; si está `failed`, mirar `sudo journalctl -u iot-puente -e` (¿token vencido? ¿InfluxDB caído? ¿credenciales del broker?).
- **Solución:** resuelta la causa, `sudo systemctl restart iot-puente`.

### Bot de Telegram caído

- **Síntoma:** no llegan alertas a "SIGEGEN Alertas" aunque haya valores fuera de umbral.
- **Diagnóstico:** `sudo systemctl status iot-bot` y `sudo journalctl -u iot-bot -e` (¿token del bot? ¿InfluxDB?).
- **Solución:** `sudo systemctl restart iot-bot`.

---

## 7. Diagnóstico rápido de conexión MQTT

Cuando un cliente (simulador o nodo) no logra conectarse al broker:

| Mensaje | Causa probable | Qué revisar |
|---------|---------------|-------------|
| `Connection refused` | Broker no corre o IP equivocada | `systemctl status mosquitto`; ¿apuntás a `100.91.59.9`? |
| `Connection timed out` | Sin ruta de red / fuera de la malla | ¿El cliente está conectado a Netbird? ¿`ping 100.91.59.9`? |
| `Not authorized` | Credenciales incorrectas | Usuario/contraseña exactos (ojo mayúsculas y espacios) |
| Mosquitto no arranca al boot | IP Netbird inexistente al momento del bind | `nonlocal_bind` en `1` (sección 5) |

---

## 8. Netbird — cuando un cliente no conecta

Si un simulador (Lenovo o Juana Manso) no llega al broker, antes de tocar MQTT verificá que el cliente esté en la malla. Desde la consola de Windows:

```
netbird status
```

| Estado | Qué significa | Qué hacer |
|--------|---------------|-----------|
| `Connected` | El túnel está arriba | Netbird no es el problema → revisar la tabla MQTT (sección 7) |
| `NeedsLogin` / "Login required" | Expiró la sesión SSO del peer | `netbird up` (abre el navegador para reautenticar) |
| El daemon no responde | El servicio de Netbird está caído | Reiniciar el cliente / el servicio de Netbird |

**Por qué aparece `NeedsLogin`:** los peers que entraron por login SSO (las laptops) tienen expiración de login (24 h por defecto). Al cumplirse, piden reautenticación. La VM `iot-server` no sufre esto porque se registró con setup key, que está exenta de la expiración.

**Para que un cliente quede siempre conectado** (sin tener que reloguear ni conectar a mano): en el dashboard de Netbird → Peers → User Devices → clic en el peer → apagar el switch **"Login Expiration"**. Alternativa: registrar el peer con una setup key. Es una decisión de seguridad consciente (baja la reautenticación periódica), razonable para el entorno de laboratorio.

---

## 9. Datos de conexión

| Recurso | Valor |
|---------|-------|
| SSH a la VM | `ssh iot-vm` |
| Broker MQTT | `100.91.59.9:1883` · usuarios `iot_user`, `esp32_node` |
| Config Mosquitto | `/etc/mosquitto/conf.d/sigegen.conf` · contraseñas en `/etc/mosquitto/passwd` |
| InfluxDB | `http://localhost:8086` · org `sigegen` · bucket `generadores` · token en `~/sigegen/token.txt` |
| Scripts | `~/sigegen/scripts/` · venv `~/sigegen-venv/` |

> ⚠️ Las contraseñas y tokens no van en este documento ni en el repo. La migración a `.env` / gestor de secretos está planificada para después de la parcial.
