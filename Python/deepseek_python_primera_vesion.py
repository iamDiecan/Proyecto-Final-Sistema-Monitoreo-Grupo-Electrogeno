#!/usr/bin/env python3
"""
Sigegen Backend - Monitoreo continuo de generadores en la provincia de Formosa
Versión: 1.0.0
Requisitos: pip install paho-mqtt influxdb-client python-dotenv
"""

import json
import logging
import os
import sys
import signal
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# ============================================================================
# Configuración desde variables de entorno
# ============================================================================

@dataclass
class MQTTConfig:
    broker: str = os.getenv("MQTT_BROKER", "localhost")
    port: int = int(os.getenv("MQTT_PORT", "1883"))
    username: Optional[str] = os.getenv("MQTT_USERNAME")
    password: Optional[str] = os.getenv("MQTT_PASSWORD")
    topic: str = os.getenv("MQTT_TOPIC", "sigegen/+/+/datos")
    qos: int = int(os.getenv("MQTT_QOS", "1"))

@dataclass
class InfluxConfig:
    url: str = os.getenv("INFLUXDB_URL", "http://localhost:8086")
    token: str = os.getenv("INFLUXDB_TOKEN", "")
    org: str = os.getenv("INFLUXDB_ORG", "sigegen")
    bucket: str = os.getenv("INFLUXDB_BUCKET", "generadores")

@dataclass
class AlarmThresholds:
    voltaje_min: float = 210.0
    voltaje_max: float = 230.0
    frecuencia_min: float = 49.5
    frecuencia_max: float = 50.5
    temp_motor_max: float = 90.0
    combustible_min_pct: float = 20.0
    rpm_min: float = 1450.0
    rpm_max: float = 1550.0
    bateria_min: float = 11.5
    rssi_min: float = -80.0
    factor_potencia_min: float = 0.85

# ============================================================================
# Configuración de logging
# ============================================================================

def setup_logging():
    """Configura logs rotativos y estructurados"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=[
            logging.FileHandler("/var/log/sigegen/backend.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("sigegen-backend")

logger = setup_logging()

# ============================================================================
# Lógica de detección de alarmas
# ============================================================================

class AlarmDetector:
    """Detecta automáticamente alarmas según umbrales definidos"""
    
    # Mapeo de códigos de alarma
    ALARM_CODES = {
        "VOLTAJE_BAJO": "voltaje_v < umbral_min",
        "VOLTAJE_ALTO": "voltaje_v > umbral_max",
        "FRECUENCIA_BAJA": "frecuencia_hz < umbral_min",
        "FRECUENCIA_ALTA": "frecuencia_hz > umbral_max",
        "TEMP_MOTOR_ALTA": "temp_motor_c > umbral_max",
        "COMBUSTIBLE_BAJO": "combustible_pct < umbral_min",
        "RPM_BAJO": "rpm < umbral_min",
        "RPM_ALTO": "rpm > umbral_max",
        "BATERIA_BAJA": "bateria_v < umbral_min",
        "SENIAL_DEBIL": "rssi_dbm < umbral_min",
        "FACTOR_POTENCIA_BAJO": "factor_potencia < umbral_min",
    }
    
    def __init__(self, thresholds: AlarmThresholds):
        self.thresholds = thresholds
    
    def detect(self, data: Dict[str, Any]) -> List[str]:
        """
        Evalúa todos los campos contra los umbrales y devuelve lista de alarmas activas.
        También actualiza el campo 'estado' del data si es necesario.
        """
        alarms = []
        
        # Volcamos las alarmas existentes si las trae el nodo (para no perderlas)
        if "alarmas" in data and isinstance(data["alarmas"], list):
            alarms = data["alarmas"].copy()
        
        # Verificar cada umbral
        if "voltaje_v" in data:
            v = data["voltaje_v"]
            if v < self.thresholds.voltaje_min:
                self._add_alarm(alarms, "VOLTAJE_BAJO")
            elif v > self.thresholds.voltaje_max:
                self._add_alarm(alarms, "VOLTAJE_ALTO")
        
        if "frecuencia_hz" in data:
            f = data["frecuencia_hz"]
            if f < self.thresholds.frecuencia_min:
                self._add_alarm(alarms, "FRECUENCIA_BAJA")
            elif f > self.thresholds.frecuencia_max:
                self._add_alarm(alarms, "FRECUENCIA_ALTA")
        
        if "temp_motor_c" in data and data["temp_motor_c"] > self.thresholds.temp_motor_max:
            self._add_alarm(alarms, "TEMP_MOTOR_ALTA")
        
        if "combustible_pct" in data and data["combustible_pct"] < self.thresholds.combustible_min_pct:
            self._add_alarm(alarms, "COMBUSTIBLE_BAJO")
        
        if "rpm" in data:
            rpm = data["rpm"]
            if rpm < self.thresholds.rpm_min:
                self._add_alarm(alarms, "RPM_BAJO")
            elif rpm > self.thresholds.rpm_max:
                self._add_alarm(alarms, "RPM_ALTO")
        
        if "bateria_v" in data and data["bateria_v"] < self.thresholds.bateria_min:
            self._add_alarm(alarms, "BATERIA_BAJA")
        
        if "rssi_dbm" in data and data["rssi_dbm"] < self.thresholds.rssi_min:
            self._add_alarm(alarms, "SENIAL_DEBIL")
        
        if "factor_potencia" in data and data["factor_potencia"] < self.thresholds.factor_potencia_min:
            self._add_alarm(alarms, "FACTOR_POTENCIA_BAJO")
        
        # Actualizar el estado general del nodo
        if alarms:
            if any(a in ["TEMP_MOTOR_ALTA", "VOLTAJE_ALTO", "VOLTAJE_BAJO", "RPM_ALTO"] for a in alarms):
                data["estado"] = "falla"
            else:
                data["estado"] = "alerta"
        else:
            data["estado"] = "normal"
        
        # Eliminar duplicados manteniendo orden
        unique_alarms = []
        for a in alarms:
            if a not in unique_alarms:
                unique_alarms.append(a)
        
        return unique_alarms
    
    def _add_alarm(self, alarms: List[str], code: str):
        """Agrega un código de alarma si no está presente"""
        if code not in alarms:
            alarms.append(code)

# ============================================================================
# Procesador de datos e InfluxDB
# ============================================================================

class InfluxWriter:
    """Maneja la escritura de datos en InfluxDB"""
    
    def __init__(self, config: InfluxConfig):
        self.config = config
        self.client = None
        self.write_api = None
        self._connect()
    
    def _connect(self):
        """Establece conexión con InfluxDB"""
        try:
            self.client = InfluxDBClient(
                url=self.config.url,
                token=self.config.token,
                org=self.config.org
            )
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            logger.info(f"Conectado a InfluxDB en {self.config.url}")
        except Exception as e:
            logger.error(f"Error conectando a InfluxDB: {e}")
            raise
    
    def write_reading(self, data: Dict[str, Any]):
        """
        Escribe una lectura completa en InfluxDB.
        Usa tags para filtrado (nodo_id, zona) y fields para valores numéricos.
        """
        nodo_id = data.get("nodo_id", "unknown")
        zona = data.get("zona", "unknown")
        timestamp_str = data.get("timestamp")
        
        # Parsear timestamp: espera ISO 8601 con Z
        if timestamp_str:
            # Normalizar: reemplazar Z por +00:00 para que Python lo entienda
            ts_str = timestamp_str.replace("Z", "+00:00")
            timestamp = datetime.fromisoformat(ts_str)
        else:
            timestamp = datetime.utcnow()
        
        # Crear punto base con tags
        point = Point("lectura_generador") \
            .tag("nodo_id", nodo_id) \
            .tag("zona", zona) \
            .time(timestamp)
        
        # Campos numéricos (mediciones)
        numeric_fields = [
            "uptime_s", "rpm", "horas_motor", "voltaje_v", "frecuencia_hz",
            "corriente_a", "potencia_kw", "factor_potencia", "temp_motor_c",
            "temp_ambiente_c", "combustible_pct", "combustible_l", "consumo_lh",
            "bateria_v", "rssi_dbm"
        ]
        
        for field in numeric_fields:
            if field in data and data[field] is not None:
                point.field(field, float(data[field]))
        
        # Campos de estado (como strings)
        if "estado" in data:
            point.field("estado", data["estado"])
        
        # Alertas: guardamos como string JSON
        if "alarmas" in data:
            point.field("alarmas", json.dumps(data["alarmas"]))
        
        # Campos de ubicación (para mapas en Grafana)
        if "lat" in data and "lon" in data:
            point.field("lat", float(data["lat"]))
            point.field("lon", float(data["lon"]))
        
        try:
            self.write_api.write(bucket=self.config.bucket, record=point)
            logger.debug(f"Dato escrito: {nodo_id} @ {timestamp}")
        except Exception as e:
            logger.error(f"Error escribiendo en InfluxDB: {e}")
    
    def close(self):
        """Cierra la conexión con InfluxDB"""
        if self.client:
            self.client.close()
            logger.info("Conexión a InfluxDB cerrada")

# ============================================================================
# Cliente MQTT principal
# ============================================================================

class SigegenBackend:
    """Backend principal que suscribe y procesa mensajes MQTT"""
    
    def __init__(self, mqtt_config: MQTTConfig, influx_config: InfluxConfig, thresholds: AlarmThresholds):
        self.mqtt_config = mqtt_config
        self.influx_writer = InfluxWriter(influx_config)
        self.alarm_detector = AlarmDetector(thresholds)
        self.client = None
        self.running = True
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback cuando se conecta al broker MQTT"""
        if rc == 0:
            logger.info(f"Conectado a MQTT broker {self.mqtt_config.broker}:{self.mqtt_config.port}")
            # Suscribirse al topic wildcard
            client.subscribe(self.mqtt_config.topic, qos=self.mqtt_config.qos)
            logger.info(f"Suscrito a: {self.mqtt_config.topic} (QoS {self.mqtt_config.qos})")
        else:
            logger.error(f"Error de conexión MQTT, código: {rc}")
    
    def on_message(self, client, userdata, msg):
        """Callback cuando llega un mensaje MQTT"""
        topic = msg.topic
        payload_str = msg.payload.decode('utf-8')
        
        logger.debug(f"Mensaje recibido en {topic}: {payload_str[:200]}...")
        
        try:
            # Parsear JSON
            data = json.loads(payload_str)
            
            # Extraer información del topic (sigegen/zona/nodo_id/tipo)
            topic_parts = topic.split('/')
            if len(topic_parts) >= 4:
                # Si el JSON ya trae zona y nodo_id, no sobreescribimos
                if "zona" not in data and topic_parts[1] != "+":
                    data["zona"] = topic_parts[1]
                if "nodo_id" not in data and topic_parts[2] != "+":
                    data["nodo_id"] = topic_parts[2]
            
            # Validar campos mínimos necesarios
            if "timestamp" not in data:
                data["timestamp"] = datetime.utcnow().isoformat() + "Z"
                logger.warning(f"Mensaje sin timestamp, se asigna actual: {data.get('nodo_id')}")
            
            # Detectar alarmas y actualizar estado
            alarmas = self.alarm_detector.detect(data)
            data["alarmas"] = alarmas
            
            # Registrar alertas importantes
            if alarmas:
                nodo = data.get("nodo_id", "unknown")
                logger.warning(f"ALARMAS en {nodo}: {', '.join(alarmas)} | estado={data.get('estado')}")
            
            # Escribir en InfluxDB
            self.influx_writer.write_reading(data)
            
            # Aquí podrías agregar lógica adicional:
            # - Enviar notificaciones (email, Telegram, webhook)
            # - Publicar mensajes a otro topic (ej: sigegen/alertas)
            # - Actualizar cache en Redis
            
        except json.JSONDecodeError as e:
            logger.error(f"Error decodificando JSON en topic {topic}: {e}")
            logger.debug(f"Payload problemático: {payload_str[:500]}")
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}", exc_info=True)
    
    def on_disconnect(self, client, userdata, rc):
        """Callback cuando se pierde la conexión MQTT"""
        if rc != 0:
            logger.warning(f"Desconexión MQTT inesperada, código: {rc}. Intentando reconectar...")
        else:
            logger.info("Desconexión MQTT solicitada")
    
    def start(self):
        """Inicia el backend y se conecta al broker MQTT"""
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        # Configurar autenticación si es necesaria
        if self.mqtt_config.username and self.mqtt_config.password:
            self.client.username_pw_set(self.mqtt_config.username, self.mqtt_config.password)
        
        # Intentar conexión con reintentos
        try:
            self.client.connect(self.mqtt_config.broker, self.mqtt_config.port, keepalive=60)
        except Exception as e:
            logger.error(f"Error conectando al broker MQTT: {e}")
            sys.exit(1)
        
        # Loop principal (bloqueante)
        self.client.loop_forever()
    
    def stop(self, signum=None, frame=None):
        """Detiene el backend limpiamente"""
        logger.info("Deteniendo backend...")
        self.running = False
        if self.client:
            self.client.disconnect()
        self.influx_writer.close()
        logger.info("Backend detenido")
        sys.exit(0)

# ============================================================================
# Punto de entrada principal
# ============================================================================

def main():
    """Función principal"""
    logger.info("=" * 60)
    logger.info("Sigegen Backend - Monitoreo de Generadores - Formosa")
    logger.info("=" * 60)
    
    # Cargar configuraciones desde environment
    mqtt_config = MQTTConfig()
    influx_config = InfluxConfig()
    thresholds = AlarmThresholds()
    
    logger.info(f"MQTT Broker: {mqtt_config.broker}:{mqtt_config.port}")
    logger.info(f"MQTT Topic: {mqtt_config.topic}")
    logger.info(f"InfluxDB URL: {influx_config.url}")
    logger.info(f"InfluxDB Bucket: {influx_config.bucket}")
    
    # Verificar configuración crítica
    if not influx_config.token:
        logger.error("INFLUXDB_TOKEN no está configurada en el archivo .env")
        sys.exit(1)
    
    # Crear y ejecutar backend
    backend = SigegenBackend(mqtt_config, influx_config, thresholds)
    
    # Manejar señales para shutdown graceful
    signal.signal(signal.SIGINT, backend.stop)
    signal.signal(signal.SIGTERM, backend.stop)
    
    try:
        backend.start()
    except KeyboardInterrupt:
        backend.stop()
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()