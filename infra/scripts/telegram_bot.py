"""
SIGEGEN — Bot de alertas Telegram
===================================
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
INFLUX_URL   = "http://localhost:8086"        # o IP Netbird si corrés remoto
INFLUX_TOKEN = open("/home/florencia/sigegen/token.txt").read().strip()
INFLUX_ORG   = "sigegen"
INFLUX_BUCKET = "generadores"

# --- Telegram ---
TELEGRAM_TOKEN  = "8736358938:AAE9bPfxNmIsPdTJVNi_zkwEw44gIhvvuV4"
TELEGRAM_CHAT_ID = "7152623429"

# --- Comportamiento ---
INTERVALO_SEGUNDOS = 60       # cada cuánto chequea
REPETIR_ALERTA     = False    # True = avisa cada vez que sigue en crítico
                              # False = avisa solo la primera vez, hasta que se normalice

# ============================================================
# UMBRALES — ajustar con el compañero de hardware (HL)
# ============================================================
# Formato: { "nombre_field": ("condicion", valor_umbral, "descripcion legible") }
# condicion puede ser "mayor" o "menor"

UMBRALES = {
    "temperatura": ("mayor", 100,  "Temperatura crítica"),   # °C
    "combustible": ("menor",  20,  "Combustible bajo"),      # %
    "rpm":         ("mayor", 1580, "RPM fuera de rango"),    # RPM
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
    query = f"""
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -2m)
      |> filter(fn: (r) => r._measurement == "generador")
      |> filter(fn: (r) => r._field == "{field}")
      |> last()
    """
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


def formatear_alerta(generador_id: str, field: str, valor, descripcion: str, condicion: str, limite) -> str:
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
    alertas_activas = set()  # conjunto de (generador_id, field)

    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)

    # Mensaje de arranque
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

                        # Mandar alerta si: no estaba activa, o si se repite siempre
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

