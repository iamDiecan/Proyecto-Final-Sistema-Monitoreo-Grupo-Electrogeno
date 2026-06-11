# sigen-backend/analytics/fuzzy_engine.py
"""
Motor de Lógica Difusa Mejorado para SIGEGEN v3.0

Extiende el sistema fuzzy existente (sigegen_fuzzy_alerts.py) con:
  - Variable de presión de aceite (Baja/Normal/Alta)
  - Variable de horas de operación (Bajas/Medias/Altas/Críticas)
  - Reglas adicionales de detección de patrones complejos
  - Sistema extensible para agregar nuevas reglas

Documentación Matemática:
══════════════════════════
Variables lingüísticas:
  - Temperatura: universo [0, 130]°C, conjuntos {Baja, Normal, Alta, Crítica}
  - Presión aceite: universo [0, 100]psi, conjuntos {Baja, Normal, Alta}
  - Voltaje: universo [180, 260]V, conjuntos {Bajo, Normal, Alto}
  - Frecuencia: universo [45, 55]Hz, conjuntos {Inestable, Normal, Inestable_alta}
  - Combustible: universo [0, 100]%, conjuntos {Bajo, Medio, Alto}
  - Horas operación: universo [0, 10000]h, conjuntos {Bajas, Medias, Altas, Críticas}

Funciones de pertenencia:
  - Triangulares (trimf): para conjuntos centrales con transiciones suaves
  - Trapezoidales (trapmf): para conjuntos extremos con saturación

Método de defuzzificación: Centroide (centro de gravedad)
  y* = ∫ y·μ(y)dy / ∫ μ(y)dy

Reglas de inferencia: Mamdani (min-max)
  - AND → operador mínimo
  - OR  → operador máximo
  - Implicación → recorte (min)
  - Agregación → máximo
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

logger = logging.getLogger("sigegen.fuzzy_engine")


class FuzzyEngineV3:
    """
    Motor de inferencia difusa v3.0 para SIGEGEN.
    Extiende las capacidades del FuzzyAlertSystem original con variables
    adicionales y reglas más complejas de detección de patrones.
    """

    def __init__(self):
        self._build_system()
        logger.info("Motor fuzzy v3.0 inicializado con %d reglas", len(self._rules))

    def _build_system(self):
        """Define variables, conjuntos difusos y reglas de inferencia."""

        # ══ VARIABLES DE ENTRADA ══════════════════════════════

        # Temperatura del motor (°C)
        self.temp = ctrl.Antecedent(np.arange(0, 131, 1), 'temperatura')
        self.temp['baja'] = fuzz.trimf(self.temp.universe, [0, 0, 50])
        self.temp['normal'] = fuzz.trimf(self.temp.universe, [40, 65, 90])
        self.temp['alta'] = fuzz.trimf(self.temp.universe, [80, 105, 120])
        self.temp['critica'] = fuzz.trapmf(self.temp.universe, [100, 115, 130, 130])

        # Presión de aceite (PSI) — NUEVA
        self.presion = ctrl.Antecedent(np.arange(0, 101, 1), 'presion_aceite')
        self.presion['baja'] = fuzz.trapmf(self.presion.universe, [0, 0, 15, 25])
        self.presion['normal'] = fuzz.trimf(self.presion.universe, [20, 40, 65])
        self.presion['alta'] = fuzz.trapmf(self.presion.universe, [55, 70, 100, 100])

        # Voltaje (V)
        self.voltaje = ctrl.Antecedent(np.arange(180, 261, 1), 'voltaje')
        self.voltaje['bajo'] = fuzz.trimf(self.voltaje.universe, [180, 195, 210])
        self.voltaje['normal'] = fuzz.trimf(self.voltaje.universe, [210, 220, 230])
        self.voltaje['alto'] = fuzz.trimf(self.voltaje.universe, [230, 245, 260])

        # Frecuencia (Hz)
        self.frecuencia = ctrl.Antecedent(np.arange(45, 55.1, 0.1), 'frecuencia')
        self.frecuencia['inestable_baja'] = fuzz.trimf(self.frecuencia.universe, [45, 47.5, 49.5])
        self.frecuencia['normal'] = fuzz.trimf(self.frecuencia.universe, [49.5, 50, 50.5])
        self.frecuencia['inestable_alta'] = fuzz.trimf(self.frecuencia.universe, [50.5, 52, 55])

        # Combustible (%)
        self.combustible = ctrl.Antecedent(np.arange(0, 101, 1), 'combustible')
        self.combustible['bajo'] = fuzz.trapmf(self.combustible.universe, [0, 0, 10, 25])
        self.combustible['medio'] = fuzz.trimf(self.combustible.universe, [20, 50, 80])
        self.combustible['alto'] = fuzz.trapmf(self.combustible.universe, [70, 85, 100, 100])

        # Horas de operación — NUEVA
        self.horas = ctrl.Antecedent(np.arange(0, 10001, 10), 'horas_operacion')
        self.horas['bajas'] = fuzz.trapmf(self.horas.universe, [0, 0, 500, 1000])
        self.horas['medias'] = fuzz.trimf(self.horas.universe, [800, 2000, 3500])
        self.horas['altas'] = fuzz.trimf(self.horas.universe, [3000, 4500, 6000])
        self.horas['criticas'] = fuzz.trapmf(self.horas.universe, [5000, 7000, 10000, 10000])

        # RPM (revoluciones por minuto) — mantenido del sistema original
        self.rpm = ctrl.Antecedent(np.arange(1300, 1701, 5), 'rpm')
        self.rpm['bajo'] = fuzz.trimf(self.rpm.universe, [1300, 1400, 1450])
        self.rpm['normal'] = fuzz.trimf(self.rpm.universe, [1450, 1500, 1550])
        self.rpm['alto'] = fuzz.trimf(self.rpm.universe, [1550, 1600, 1700])

        # Vibración (mm/s)
        self.vibracion = ctrl.Antecedent(np.arange(0, 20.5, 0.5), 'vibracion')
        self.vibracion['baja'] = fuzz.trimf(self.vibracion.universe, [0, 0, 3])
        self.vibracion['normal'] = fuzz.trimf(self.vibracion.universe, [2, 4, 6])
        self.vibracion['alta'] = fuzz.trimf(self.vibracion.universe, [5, 8, 12])
        self.vibracion['critica'] = fuzz.trapmf(self.vibracion.universe, [10, 14, 20, 20])

        # ══ VARIABLE DE SALIDA ════════════════════════════════

        self.riesgo = ctrl.Consequent(np.arange(0, 101, 1), 'riesgo')
        self.riesgo['bajo'] = fuzz.trimf(self.riesgo.universe, [0, 0, 25])
        self.riesgo['moderado'] = fuzz.trimf(self.riesgo.universe, [15, 35, 55])
        self.riesgo['alto'] = fuzz.trimf(self.riesgo.universe, [45, 65, 85])
        self.riesgo['critico'] = fuzz.trapmf(self.riesgo.universe, [75, 90, 100, 100])

        # ══ REGLAS DE INFERENCIA ══════════════════════════════

        self._rules = []

        # R1: Temperatura alta + Presión baja → riesgo alto (sobrecalentamiento)
        self._rules.append(
            ctrl.Rule(self.temp['alta'] & self.presion['baja'], self.riesgo['alto'])
        )

        # R2: Frecuencia inestable + Voltaje fuera de rango → riesgo alto (regulación)
        self._rules.append(
            ctrl.Rule(
                (self.frecuencia['inestable_baja'] | self.frecuencia['inestable_alta']) &
                (self.voltaje['bajo'] | self.voltaje['alto']),
                self.riesgo['alto']
            )
        )

        # R3: Combustible bajo + Horas altas → riesgo moderado (operativo)
        self._rules.append(
            ctrl.Rule(self.combustible['bajo'] & self.horas['altas'], self.riesgo['alto'])
        )

        # R4: Temperatura crítica → riesgo crítico (emergencia)
        self._rules.append(
            ctrl.Rule(self.temp['critica'], self.riesgo['critico'])
        )

        # R5: Presión baja crítica → riesgo crítico (daño motor inminente)
        self._rules.append(
            ctrl.Rule(self.presion['baja'] & self.temp['alta'], self.riesgo['critico'])
        )

        # R6: Todo normal → riesgo bajo
        self._rules.append(
            ctrl.Rule(
                self.temp['normal'] & self.voltaje['normal'] &
                self.frecuencia['normal'] & self.combustible['medio'] &
                self.rpm['normal'] & self.vibracion['normal'],
                self.riesgo['bajo']
            )
        )

        # R7: Combustible bajo aislado → riesgo moderado
        self._rules.append(
            ctrl.Rule(self.combustible['bajo'] & self.temp['normal'], self.riesgo['moderado'])
        )

        # R8: RPM anormal → riesgo moderado
        self._rules.append(
            ctrl.Rule(self.rpm['bajo'] | self.rpm['alto'], self.riesgo['moderado'])
        )

        # R9: Frecuencia fuera de rango aislada → riesgo moderado
        self._rules.append(
            ctrl.Rule(
                self.frecuencia['inestable_baja'] | self.frecuencia['inestable_alta'],
                self.riesgo['moderado']
            )
        )

        # R10: Voltaje alto + Frecuencia alta (sobrecarga) → riesgo alto
        self._rules.append(
            ctrl.Rule(
                self.voltaje['alto'] & self.frecuencia['inestable_alta'],
                self.riesgo['alto']
            )
        )

        # R11: Vibración alta + RPM alto → riesgo alto
        self._rules.append(
            ctrl.Rule(self.vibracion['alta'] & self.rpm['alto'], self.riesgo['alto'])
        )

        # R12: Vibración crítica → riesgo crítico
        self._rules.append(
            ctrl.Rule(self.vibracion['critica'], self.riesgo['critico'])
        )

        # R13: Horas críticas + Temperatura alta → riesgo crítico
        self._rules.append(
            ctrl.Rule(self.horas['criticas'] & self.temp['alta'], self.riesgo['critico'])
        )

        # R14: Múltiples anomalías combinadas → riesgo alto
        self._rules.append(
            ctrl.Rule(
                (self.temp['alta'] | self.rpm['bajo'] | self.rpm['alto']) &
                (self.combustible['bajo']),
                self.riesgo['alto']
            )
        )

        # R15: Horas altas + Combustible bajo → riesgo alto
        self._rules.append(
            ctrl.Rule(self.horas['altas'] & self.combustible['bajo'], self.riesgo['alto'])
        )

        # Crear sistema de control
        self._ctrl_system = ctrl.ControlSystem(self._rules)
        self._simulation = ctrl.ControlSystemSimulation(self._ctrl_system)

    def evaluate(self, data: Dict[str, Any]) -> Tuple[float, str, Dict[str, float]]:
        """
        Evalúa los sensores y calcula el nivel de riesgo.

        Args:
            data: Diccionario con lecturas del generador.

        Returns:
            (nivel_riesgo, clasificacion, contribuciones)
            - nivel_riesgo: float 0-100
            - clasificacion: "INFO" | "WARNING" | "CRITICAL"
            - contribuciones: dict con score 0-100 por variable
        """
        # Extraer y clampar valores
        temp = max(0, min(130, float(data.get('temp_motor_c', 65) or 65)))
        presion = max(0, min(100, float(data.get('presion_aceite_psi', 40) or 40)))
        volt = max(180, min(260, float(data.get('voltaje_v', 220) or 220)))
        freq = max(45, min(55, float(data.get('frecuencia_hz', 50) or 50)))
        comb = max(0, min(100, float(data.get('combustible_pct', 50) or 50)))
        horas = max(0, min(10000, float(data.get('horas_motor', 0) or 0)))
        rpm_val = max(1300, min(1700, float(data.get('rpm', 1500) or 1500)))
        vib = max(0, min(20, float(data.get('vibracion_mms', 3) or 3)))

        try:
            self._simulation.input['temperatura'] = temp
            self._simulation.input['presion_aceite'] = presion
            self._simulation.input['voltaje'] = volt
            self._simulation.input['frecuencia'] = freq
            self._simulation.input['combustible'] = comb
            self._simulation.input['horas_operacion'] = horas
            self._simulation.input['rpm'] = rpm_val
            self._simulation.input['vibracion'] = vib

            self._simulation.compute()
            nivel = float(self._simulation.output['riesgo'])
        except Exception as e:
            logger.error("Error en evaluación fuzzy v3: %s", e)
            nivel = 50.0

        # Clasificar
        if nivel >= 65:
            clasificacion = "CRITICAL"
        elif nivel >= 35:
            clasificacion = "WARNING"
        else:
            clasificacion = "INFO"

        # Contribuciones
        contribuciones = self._calcular_contribuciones(data)

        return round(nivel, 2), clasificacion, contribuciones

    def _calcular_contribuciones(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calcula la contribución al riesgo de cada variable (0-100)."""
        contrib = {}

        temp = float(data.get('temp_motor_c', 65) or 65)
        if temp > 90:
            contrib['temperatura'] = min(100, (temp - 90) / 30 * 100)
        elif temp > 80:
            contrib['temperatura'] = (temp - 80) / 10 * 50
        else:
            contrib['temperatura'] = 0

        presion = float(data.get('presion_aceite_psi', 40) or 40)
        if presion < 25:
            contrib['presion_aceite'] = min(100, (25 - presion) / 25 * 100)
        else:
            contrib['presion_aceite'] = 0

        volt = float(data.get('voltaje_v', 220) or 220)
        if volt < 210:
            contrib['voltaje'] = min(100, (210 - volt) / 30 * 100)
        elif volt > 230:
            contrib['voltaje'] = min(100, (volt - 230) / 30 * 100)
        else:
            contrib['voltaje'] = 0

        freq = float(data.get('frecuencia_hz', 50) or 50)
        if freq < 49.5:
            contrib['frecuencia'] = min(100, (49.5 - freq) / 4.5 * 100)
        elif freq > 50.5:
            contrib['frecuencia'] = min(100, (freq - 50.5) / 4.5 * 100)
        else:
            contrib['frecuencia'] = 0

        comb = float(data.get('combustible_pct', 50) or 50)
        if comb < 25:
            contrib['combustible'] = min(100, (25 - comb) / 25 * 100)
        else:
            contrib['combustible'] = 0

        rpm_val = float(data.get('rpm', 1500) or 1500)
        if rpm_val < 1450:
            contrib['rpm'] = min(100, (1450 - rpm_val) / 150 * 100)
        elif rpm_val > 1550:
            contrib['rpm'] = min(100, (rpm_val - 1550) / 150 * 100)
        else:
            contrib['rpm'] = 0

        horas = float(data.get('horas_motor', 0) or 0)
        if horas > 5000:
            contrib['horas_operacion'] = min(100, (horas - 5000) / 5000 * 100)
        elif horas > 3000:
            contrib['horas_operacion'] = (horas - 3000) / 2000 * 50
        else:
            contrib['horas_operacion'] = 0

        return contrib


# ── Instancia singleton ──────────────────────────────────────
_engine_instance: Optional[FuzzyEngineV3] = None


def get_fuzzy_engine() -> FuzzyEngineV3:
    """Retorna la instancia singleton del motor fuzzy v3."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = FuzzyEngineV3()
    return _engine_instance
