#!/usr/bin/env python3
"""
Sigegen Backend - Monitoreo continuo de generadores en la provincia de Formosa
Versión: 2.0.0 - Con Sistema de Alertas Difuso Integrado
"""

import json
import logging
import os
import sys
import signal
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Tuple

import paho.mqtt.client as mqtt
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


# CONFIGURACIÓN


MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "sigegen/+/+/datos")
MQTT_QOS = int(os.getenv("MQTT_QOS", "1"))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
)
logger = logging.getLogger("sigegen-backend")


# SISTEMA DE ALERTAS DIFUSO


class FuzzyAlertSystem:
    """
    Sistema de inferencia difusa para evaluar estado de generadores
    """
    
    def __init__(self):
        self._setup_fuzzy_system()
        logger.info("Sistema de alertas difuso inicializado")
    
    def _setup_fuzzy_system(self):
        """Define las variables y reglas difusas"""
        
        
        # VARIABLES DE ENTRADA
        
        
        # Temperatura del motor (°C)
        self.temp = ctrl.Antecedent(np.arange(0, 130, 1), 'temperatura')
        self.temp['baja'] = fuzz.trimf(self.temp.universe, [0, 0, 50])
        self.temp['normal'] = fuzz.trimf(self.temp.universe, [40, 65, 90])
        self.temp['alta'] = fuzz.trimf(self.temp.universe, [80, 105, 120])
        self.temp['critica'] = fuzz.trapmf(self.temp.universe, [100, 115, 130, 130])
        
        # Voltaje (V)
        self.voltaje = ctrl.Antecedent(np.arange(180, 260, 1), 'voltaje')
        self.voltaje['bajo'] = fuzz.trimf(self.voltaje.universe, [180, 195, 210])
        self.voltaje['normal'] = fuzz.trimf(self.voltaje.universe, [210, 220, 230])
        self.voltaje['alto'] = fuzz.trimf(self.voltaje.universe, [230, 245, 260])
        
        # Frecuencia (Hz)
        self.frecuencia = ctrl.Antecedent(np.arange(45, 55, 0.1), 'frecuencia')
        self.frecuencia['baja'] = fuzz.trimf(self.frecuencia.universe, [45, 47.5, 49.5])
        self.frecuencia['normal'] = fuzz.trimf(self.frecuencia.universe, [49.5, 50, 50.5])
        self.frecuencia['alta'] = fuzz.trimf(self.frecuencia.universe, [50.5, 52, 55])
        
        # Combustible (%)
        self.combustible = ctrl.Antecedent(np.arange(0, 101, 1), 'combustible')
        self.combustible['critico'] = fuzz.trapmf(self.combustible.universe, [0, 0, 5, 10])
        self.combustible['bajo'] = fuzz.trimf(self.combustible.universe, [5, 12, 25])
        self.combustible['normal'] = fuzz.trimf(self.combustible.universe, [20, 50, 80])
        self.combustible['alto'] = fuzz.trimf(self.combustible.universe, [70, 85, 100])
        
        # RPM (revoluciones por minuto)
        self.rpm = ctrl.Antecedent(np.arange(1300, 1700, 5), 'rpm')
        self.rpm['bajo'] = fuzz.trimf(self.rpm.universe, [1300, 1400, 1450])
        self.rpm['normal'] = fuzz.trimf(self.rpm.universe, [1450, 1500, 1550])
        self.rpm['alto'] = fuzz.trimf(self.rpm.universe, [1550, 1600, 1700])
        
        
        # VARIABLE DE SALIDA (Nivel de Alerta)
        
        
        self.alerta = ctrl.Consequent(np.arange(0, 101, 1), 'alerta')
        self.alerta['normal'] = fuzz.trimf(self.alerta.universe, [0, 0, 25])
        self.alerta['precaucion'] = fuzz.trimf(self.alerta.universe, [15, 30, 45])
        self.alerta['alerta'] = fuzz.trimf(self.alerta.universe, [35, 50, 65])
        self.alerta['critico'] = fuzz.trimf(self.alerta.universe, [55, 70, 85])
        self.alerta['emergencia'] = fuzz.trapmf(self.alerta.universe, [75, 90, 100, 100])
        
        
        # REGLAS DIFUSAS
        
        
        # Regla 1: Temperatura crítica (sin importar otras variables)
        rule1 = ctrl.Rule(self.temp['critica'], self.alerta['emergencia'])
        
        # Regla 2: Temperatura alta + voltaje bajo
        rule2 = ctrl.Rule(self.temp['alta'] & self.voltaje['bajo'], 
                          self.alerta['critico'])
        
        # Regla 3: Combustible crítico
        rule3 = ctrl.Rule(self.combustible['critico'], self.alerta['emergencia'])
        
        # Regla 4: Combustible bajo + RPM anormal
        rule4 = ctrl.Rule(self.combustible['bajo'] & (self.rpm['bajo'] | self.rpm['alto']), 
                          self.alerta['alerta'])
        
        # Regla 5: RPM inestable
        rule5 = ctrl.Rule(self.rpm['bajo'] | self.rpm['alto'], 
                          self.alerta['precaucion'])
        
        # Regla 6: Frecuencia fuera de rango
        rule6 = ctrl.Rule(self.frecuencia['baja'] | self.frecuencia['alta'], 
                          self.alerta['alerta'])
        
        # Regla 7: Voltaje alto + frecuencia alta (sobrecarga)
        rule7 = ctrl.Rule(self.voltaje['alto'] & self.frecuencia['alta'], 
                          self.alerta['critico'])
        
        # Regla 8: Todo normal
        rule8 = ctrl.Rule(self.temp['normal'] & self.voltaje['normal'] & 
                          self.frecuencia['normal'] & self.rpm['normal'] & 
                          ~self.combustible['critico'],
                          self.alerta['normal'])
        
        # Regla 9: Múltiples condiciones anómalas
        rule9 = ctrl.Rule((self.temp['alta'] | self.rpm['bajo'] | self.rpm['alto']) & 
                          (self.combustible['bajo'] | self.combustible['critico']),
                          self.alerta['critico'])
        
        # Regla 10: Temperatura alta + RPM bajo
        rule10 = ctrl.Rule(self.temp['alta'] & self.rpm['bajo'],
                           self.alerta['alerta'])
        
        # Crear sistema de control
        self.alerta_ctrl = ctrl.ControlSystem([
            rule1, rule2, rule3, rule4, rule5, rule6,
            rule7, rule8, rule9, rule10
        ])
        
        self.alerta_sim = ctrl.ControlSystemSimulation(self.alerta_ctrl)
    
    def evaluate(self, datos: Dict[str, Any]) -> Tuple[float, str, Dict[str, float]]:
        """
        Evalúa los sensores y calcula nivel de alerta difusa
        
        Returns:
            (nivel_alerta, categoria, detalles)
        """
        # Valores por defecto
        temp = datos.get('temp_motor_c', 65)
        volt = datos.get('voltaje_v', 220)
        freq = datos.get('frecuencia_hz', 50)
        comb = datos.get('combustible_pct', 50)
        rpm_val = datos.get('rpm', 1500)
        
        # Limitar valores a rangos definidos
        temp = max(0, min(130, temp))
        volt = max(180, min(260, volt))
        freq = max(45, min(55, freq))
        comb = max(0, min(100, comb))
        rpm_val = max(1300, min(1700, rpm_val))
        
        try:
            self.alerta_sim.input['temperatura'] = temp
            self.alerta_sim.input['voltaje'] = volt
            self.alerta_sim.input['frecuencia'] = freq
            self.alerta_sim.input['combustible'] = comb
            self.alerta_sim.input['rpm'] = rpm_val
            
            self.alerta_sim.compute()
            nivel = self.alerta_sim.output['alerta']
            
        except Exception as e:
            logger.error(f"Error en evaluación difusa: {e}")
            nivel = 50
        
        # Determinar categoría
        if nivel < 15:
            categoria = "normal"
        elif nivel < 35:
            categoria = "precaucion"
        elif nivel < 60:
            categoria = "alerta"
        elif nivel < 85:
            categoria = "critico"
        else:
            categoria = "emergencia"
        
        # Calcular contribuciones
        contribuciones = self._calcular_contribuciones(datos)
        
        return round(nivel, 2), categoria, contribuciones
    
    def _calcular_contribuciones(self, datos: Dict[str, Any]) -> Dict[str, float]:
        """Calcula contribución de cada variable al nivel de alerta"""
        contribuciones = {}
        
        temp = datos.get('temp_motor_c', 65)
        if temp > 90:
            contribuciones['temperatura'] = min(100, (temp - 90) / 30 * 100)
        elif temp > 80:
            contribuciones['temperatura'] = (temp - 80) / 10 * 50
        else:
            contribuciones['temperatura'] = 0
        
        volt = datos.get('voltaje_v', 220)
        if volt < 210:
            contribuciones['voltaje'] = min(100, (210 - volt) / 30 * 100)
        elif volt > 230:
            contribuciones['voltaje'] = min(100, (volt - 230) / 30 * 100)
        else:
            contribuciones['voltaje'] = 0
        
        comb = datos.get('combustible_pct', 50)
        if comb < 20:
            contribuciones['combustible'] = min(100, (20 - comb) / 20 * 100)
        else:
            contribuciones['combustible'] = 0
        
        rpm_val = datos.get('rpm', 1500)
        if rpm_val < 1450:
            contribuciones['rpm'] = min(100, (1450 - rpm_val) / 150 * 100)
        elif rpm_val > 1550:
            contribuciones['rpm'] = min(100, (rpm_val - 1550) / 150 * 100)
        else:
            contribuciones['rpm'] = 0
        
        return contribuciones



# BASE DE DATOS SQLITE


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('sigegen.db', check_same_thread=False)
        self.create_tables()
        logger.info("Base de datos SQLite inicializada")
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lecturas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                nodo_id TEXT,
                zona TEXT,
                ubicacion TEXT,
                lat REAL,
                lon REAL,
                uptime_s INTEGER,
                encendido INTEGER,
                rpm REAL,
                horas_motor REAL,
                voltaje_v REAL,
                frecuencia_hz REAL,
                corriente_a REAL,
                potencia_kw REAL,
                factor_potencia REAL,
                temp_motor_c REAL,
                temp_ambiente_c REAL,
                combustible_pct REAL,
                combustible_l REAL,
                consumo_lh REAL,
                bateria_v REAL,
                estado TEXT,
                alarmas TEXT,
                alerta_difusa_nivel REAL,
                alerta_difusa_categoria TEXT,
                rssi_dbm INTEGER,
                fw_version TEXT
            )
        ''')
        self.conn.commit()
    
    def insert_reading(self, data: Dict[str, Any]):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO lecturas (
                timestamp, nodo_id, zona, ubicacion, lat, lon,
                uptime_s, encendido, rpm, horas_motor, voltaje_v,
                frecuencia_hz, corriente_a, potencia_kw, factor_potencia,
                temp_motor_c, temp_ambiente_c, combustible_pct, combustible_l,
                consumo_lh, bateria_v, estado, alarmas,
                alerta_difusa_nivel, alerta_difusa_categoria,
                rssi_dbm, fw_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get("timestamp"), data.get("nodo_id"), data.get("zona"),
            data.get("ubicacion"), data.get("lat"), data.get("lon"),
            data.get("uptime_s"), 1 if data.get("encendido") else 0,
            data.get("rpm"), data.get("horas_motor"), data.get("voltaje_v"),
            data.get("frecuencia_hz"), data.get("corriente_a"), data.get("potencia_kw"),
            data.get("factor_potencia"), data.get("temp_motor_c"), data.get("temp_ambiente_c"),
            data.get("combustible_pct"), data.get("combustible_l"), data.get("consumo_lh"),
            data.get("bateria_v"), data.get("estado"), json.dumps(data.get("alarmas", [])),
            data.get("alerta_difusa_nivel"), data.get("alerta_difusa_categoria"),
            data.get("rssi_dbm"), data.get("fw_version")
        ))
        self.conn.commit()
    
    def close(self):
        self.conn.close()



# BACKEND PRINCIPAL


class SigegenBackend:
    """Backend principal con sistema de alertas difuso"""
    
    def __init__(self):
        self.db = Database()
        self.fuzzy = FuzzyAlertSystem()
        self.client = None
        self.running = True
    
    def _detectar_alarmas_tradicionales(self, datos: Dict[str, Any]) -> List[str]:
        """Detecta alarmas por umbrales tradicionales"""
        alarmas = []
        
        if datos.get('temp_motor_c', 0) > 90:
            alarmas.append("TEMP_ALTA")
        
        volt = datos.get('voltaje_v', 220)
        if volt < 210:
            alarmas.append("VOLTAJE_BAJO")
        elif volt > 230:
            alarmas.append("VOLTAJE_ALTO")
        
        if datos.get('combustible_pct', 100) < 20:
            alarmas.append("COMBUSTIBLE_BAJO")
        
        rpm = datos.get('rpm', 1500)
        if rpm < 1450:
            alarmas.append("RPM_BAJO")
        elif rpm > 1550:
            alarmas.append("RPM_ALTO")
        
        freq = datos.get('frecuencia_hz', 50)
        if freq < 49.5:
            alarmas.append("FRECUENCIA_BAJA")
        elif freq > 50.5:
            alarmas.append("FRECUENCIA_ALTA")
        
        return alarmas
    
    def procesar_lectura(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa una lectura con el sistema difuso"""
        
        # Evaluar con lógica difusa
        nivel, categoria, contribuciones = self.fuzzy.evaluate(datos)
        
        # Agregar al payload
        datos['alerta_difusa_nivel'] = nivel
        datos['alerta_difusa_categoria'] = categoria
        
        # Detectar alarmas tradicionales
        alarmas_tradicionales = self._detectar_alarmas_tradicionales(datos)
        
        # Combinar: si nivel difuso es alto, agregar alarma
        if nivel >= 60:
            alarmas_tradicionales.append(f"DIFUSO_{categoria.upper()}")
        
        datos['alarmas'] = list(set(alarmas_tradicionales))
        
        # Actualizar estado según nivel difuso
        if nivel >= 75:
            datos['estado'] = "falla"
        elif nivel >= 35:
            datos['estado'] = "alerta"
        else:
            datos['estado'] = "normal"
        
        return datos
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"Conectado a MQTT broker {MQTT_BROKER}:{MQTT_PORT}")
            client.subscribe(MQTT_TOPIC, qos=MQTT_QOS)
            logger.info(f"Suscrito a: {MQTT_TOPIC}")
        else:
            logger.error(f"Error de conexión MQTT, código: {rc}")
    
    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload_str = msg.payload.decode('utf-8')
        
        try:
            datos = json.loads(payload_str)
            
            # Extraer datos del topic
            topic_parts = topic.split('/')
            if len(topic_parts) >= 4:
                if "zona" not in datos:
                    datos["zona"] = topic_parts[1]
                if "nodo_id" not in datos:
                    datos["nodo_id"] = topic_parts[2]
            
            # Asegurar timestamp
            if "timestamp" not in datos:
                datos["timestamp"] = datetime.utcnow().isoformat() + "Z"
            
            # Procesar con sistema difuso
            datos = self.procesar_lectura(datos)
            
            # Guardar en base de datos
            self.db.insert_reading(datos)
            
            nodo = datos.get("nodo_id", "unknown")
            nivel = datos.get("alerta_difusa_nivel", 0)
            categoria = datos.get("alerta_difusa_categoria", "normal")
            
            if nivel >= 60:
                logger.warning(f"ALERTA DIFUSA en {nodo}: nivel={nivel}, categoria={categoria}, alarmas={datos.get('alarmas')}")
            elif nivel >= 35:
                logger.info(f"PRECAUCION en {nodo}: nivel={nivel}, categoria={categoria}")
            else:
                logger.info(f"Lectura normal de {nodo}: T={datos.get('temp_motor_c')}°C, V={datos.get('voltaje_v')}V, nivel={nivel}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Error decodificando JSON: {e}")
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}", exc_info=True)
    
    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            logger.warning(f"Desconexión MQTT inesperada, código: {rc}")
        else:
            logger.info("Desconexión MQTT solicitada")
    
    def start(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        if MQTT_USERNAME and MQTT_PASSWORD:
            self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        
        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            logger.info(f"Conectando a {MQTT_BROKER}:{MQTT_PORT}...")
            self.client.loop_forever()
        except Exception as e:
            logger.error(f"Error conectando al broker MQTT: {e}")
            sys.exit(1)
    
    def stop(self, signum=None, frame=None):
        logger.info("Deteniendo backend...")
        self.running = False
        if self.client:
            self.client.disconnect()
        self.db.close()
        logger.info("Backend detenido")
        sys.exit(0)



# PUNTO DE ENTRADA


def main():
    logger.info("=" * 60)
    logger.info("Sigegen Backend v2.0 - Sistema de Alertas Difuso")
    logger.info("Monitoreo de Generadores - Provincia de Formosa")
    logger.info("=" * 60)
    
    logger.info(f"MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
    logger.info(f"MQTT Topic: {MQTT_TOPIC}")
    
    backend = SigegenBackend()
    
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