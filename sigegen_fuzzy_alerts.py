#!/usr/bin/env python3
"""
Sistema de Alertas Difusas para Sigegen
Evalúa múltiples sensores y calcula nivel de alerta (0-100)
"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger("sigegen-fuzzy")

class FuzzyAlertSystem:
    """
    Sistema de inferencia difusa para evaluar estado de generadores
    """
    
    def __init__(self):
        self._setup_fuzzy_system()
        
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
        
        # Vibración (mm/s) - nuevo sensor sugerido
        self.vibracion = ctrl.Antecedent(np.arange(0, 20, 0.5), 'vibracion')
        self.vibracion['baja'] = fuzz.trimf(self.vibracion.universe, [0, 0, 3])
        self.vibracion['normal'] = fuzz.trimf(self.vibracion.universe, [2, 4, 6])
        self.vibracion['alta'] = fuzz.trimf(self.vibracion.universe, [5, 8, 12])
        self.vibracion['critica'] = fuzz.trapmf(self.vibracion.universe, [10, 14, 20, 20])
        
        
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
        
        # Regla 3: Temperatura alta + vibración alta
        rule3 = ctrl.Rule(self.temp['alta'] & self.vibracion['alta'], 
                          self.alerta['critico'])
        
        # Regla 4: Combustible crítico
        rule4 = ctrl.Rule(self.combustible['critico'], self.alerta['emergencia'])
        
        # Regla 5: Combustible bajo + cualquier anomalía
        rule5 = ctrl.Rule(self.combustible['bajo'] & (self.rpm['bajo'] | self.rpm['alto']), 
                          self.alerta['alerta'])
        
        # Regla 6: Combustible bajo + temperatura normal
        rule6 = ctrl.Rule(self.combustible['bajo'] & self.temp['normal'], 
                          self.alerta['precaucion'])
        
        # Regla 7: RPM inestable (oscila entre bajo y alto) - se detecta con histórico
        rule7 = ctrl.Rule(self.rpm['bajo'] | self.rpm['alto'], 
                          self.alerta['precaucion'])
        
        # Regla 8: RPM + vibración altas
        rule8 = ctrl.Rule(self.rpm['alto'] & self.vibracion['alta'], 
                          self.alerta['critico'])
        
        # Regla 9: Frecuencia fuera de rango
        rule9 = ctrl.Rule(self.frecuencia['baja'] | self.frecuencia['alta'], 
                          self.alerta['alerta'])
        
        # Regla 10: Voltaje alto + frecuencia alta (sobrecarga)
        rule10 = ctrl.Rule(self.voltaje['alto'] & self.frecuencia['alta'], 
                           self.alerta['critico'])
        
        # Regla 11: Todo normal
        rule11 = ctrl.Rule(self.temp['normal'] & self.voltaje['normal'] & 
                           self.frecuencia['normal'] & self.rpm['normal'] & 
                           self.vibracion['normal'] & ~self.combustible['critico'],
                           self.alerta['normal'])
        
        # Regla 12: Múltiples condiciones anómalas
        rule12 = ctrl.Rule((self.temp['alta'] | self.rpm['bajo'] | self.rpm['alto']) & 
                           (self.combustible['bajo'] | self.combustible['critico']),
                           self.alerta['critico'])
        
        # Crear sistema de control
        self.alerta_ctrl = ctrl.ControlSystem([
            rule1, rule2, rule3, rule4, rule5, rule6,
            rule7, rule8, rule9, rule10, rule11, rule12
        ])
        
        self.alerta_sim = ctrl.ControlSystemSimulation(self.alerta_ctrl)
        
        logger.info("Sistema de alertas difuso inicializado con 12 reglas")
    
    def evaluate(self, datos: Dict[str, Any]) -> Tuple[float, str, Dict[str, float]]:
        """
        Evalúa los sensores y calcula nivel de alerta difusa
        
        Args:
            datos: Diccionario con lecturas del generador
            
        Returns:
            (nivel_alerta, categoria, detalles)
        """
        # Valores por defecto si no hay sensor
        temp = datos.get('temp_motor_c', 65)
        volt = datos.get('voltaje_v', 220)
        freq = datos.get('frecuencia_hz', 50)
        comb = datos.get('combustible_pct', 50)
        rpm_val = datos.get('rpm', 1500)
        vib = datos.get('vibracion_mms', 3)  # Nuevo sensor opcional
        
        # Limitar valores a rangos definidos
        temp = max(0, min(130, temp))
        volt = max(180, min(260, volt))
        freq = max(45, min(55, freq))
        comb = max(0, min(100, comb))
        rpm_val = max(1300, min(1700, rpm_val))
        vib = max(0, min(20, vib))
        
        try:
            # Ejecutar simulación difusa
            self.alerta_sim.input['temperatura'] = temp
            self.alerta_sim.input['voltaje'] = volt
            self.alerta_sim.input['frecuencia'] = freq
            self.alerta_sim.input['combustible'] = comb
            self.alerta_sim.input['rpm'] = rpm_val
            self.alerta_sim.input['vibracion'] = vib
            
            self.alerta_sim.compute()
            
            nivel = self.alerta_sim.output['alerta']
            
        except Exception as e:
            logger.error(f"Error en evaluación difusa: {e}")
            nivel = 50  # Valor por defecto en caso de error
        
        # Determinar categoría según nivel
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
        
        # Calcular contribución de cada variable (para diagnóstico)
        contribuciones = self._calcular_contribuciones(datos)
        
        return round(nivel, 2), categoria, contribuciones
    
    def _calcular_contribuciones(self, datos: Dict[str, Any]) -> Dict[str, float]:
        """
        Calcula qué tan cerca está cada variable de activar una alerta
        Retorna un score 0-100 por variable
        """
        contribuciones = {}
        
        # Temperatura
        temp = datos.get('temp_motor_c', 65)
        if temp > 90:
            contribuciones['temp'] = min(100, (temp - 90) / 30 * 100)
        elif temp > 80:
            contribuciones['temp'] = (temp - 80) / 10 * 50
        else:
            contribuciones['temp'] = 0
        
        # Voltaje
        volt = datos.get('voltaje_v', 220)
        if volt < 210:
            contribuciones['voltaje'] = min(100, (210 - volt) / 30 * 100)
        elif volt > 230:
            contribuciones['voltaje'] = min(100, (volt - 230) / 30 * 100)
        else:
            contribuciones['voltaje'] = 0
        
        # Combustible
        comb = datos.get('combustible_pct', 50)
        if comb < 20:
            contribuciones['combustible'] = min(100, (20 - comb) / 20 * 100)
        else:
            contribuciones['combustible'] = 0
        
        # RPM
        rpm_val = datos.get('rpm', 1500)
        if rpm_val < 1450:
            contribuciones['rpm'] = min(100, (1450 - rpm_val) / 150 * 100)
        elif rpm_val > 1550:
            contribuciones['rpm'] = min(100, (rpm_val - 1550) / 150 * 100)
        else:
            contribuciones['rpm'] = 0
        
        return contribuciones



# INTEGRACIÓN CON EL BACKEND EXISTENTE


class SigegenBackendConFuzzy:
    """
    Backend mejorado con sistema de alertas difuso
    """
    
    def __init__(self):
        self.fuzzy_alerts = FuzzyAlertSystem()
        
    def procesar_lectura(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa una lectura y agrega alerta difusa
        """
        # Evaluar con lógica difusa
        nivel, categoria, contribuciones = self.fuzzy_alerts.evaluate(datos)
        
        # Agregar al payload
        datos['alerta_difusa_nivel'] = nivel
        datos['alerta_difusa_categoria'] = categoria
        datos['alerta_difusa_contribuciones'] = contribuciones
        
        # Mantener alarmas tradicionales para compatibilidad
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
    
    def _detectar_alarmas_tradicionales(self, datos: Dict[str, Any]) -> list:
        """Mantiene las alarmas por umbral del sistema original"""
        alarmas = []
        
        # Temperatura
        if datos.get('temp_motor_c', 0) > 90:
            alarmas.append("TEMP_ALTA")
        
        # Voltaje
        volt = datos.get('voltaje_v', 220)
        if volt < 210:
            alarmas.append("VOLTAJE_BAJO")
        elif volt > 230:
            alarmas.append("VOLTAJE_ALTO")
        
        # Combustible
        if datos.get('combustible_pct', 100) < 20:
            alarmas.append("COMBUSTIBLE_BAJO")
        
        # RPM
        rpm = datos.get('rpm', 1500)
        if rpm < 1450:
            alarmas.append("RPM_BAJO")
        elif rpm > 1550:
            alarmas.append("RPM_ALTO")
        
        return alarmas



# EJEMPLO DE USO


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Inicializar sistema
    sistema = SigegenBackendConFuzzy()
    
    # Ejemplos de prueba
    casos_prueba = [
        {"temp_motor_c": 65, "voltaje_v": 220, "combustible_pct": 80, "rpm": 1500, "vibracion_mms": 2},
        {"temp_motor_c": 85, "voltaje_v": 215, "combustible_pct": 60, "rpm": 1480, "vibracion_mms": 4},
        {"temp_motor_c": 95, "voltaje_v": 205, "combustible_pct": 40, "rpm": 1460, "vibracion_mms": 6},
        {"temp_motor_c": 105, "voltaje_v": 200, "combustible_pct": 15, "rpm": 1420, "vibracion_mms": 10},
        {"temp_motor_c": 75, "voltaje_v": 235, "combustible_pct": 10, "rpm": 1510, "vibracion_mms": 3},
        {"temp_motor_c": 60, "voltaje_v": 225, "combustible_pct": 5, "rpm": 1520, "vibracion_mms": 2},
    ]
    
    print("\n" + "="*80)
    print("SISTEMA DE ALERTAS DIFUSAS - SIGEGEN")
    print("="*80)
    
    for i, caso in enumerate(casos_prueba, 1):
        resultado = sistema.procesar_lectura(caso)
        
        print(f"\n--- Caso {i} ---")
        print(f"  Entrada: T={caso['temp_motor_c']}°C, V={caso['voltaje_v']}V, "
              f"Comb={caso['combustible_pct']}%, RPM={caso['rpm']}")
        print(f"  Alerta difusa: {resultado['alerta_difusa_nivel']:.1f} / 100 ({resultado['alerta_difusa_categoria']})")
        print(f"  Contribuciones: {resultado['alerta_difusa_contribuciones']}")
        print(f"  Estado final: {resultado['estado']}")
        print(f"  Alarmas: {resultado['alarmas']}")