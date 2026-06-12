# sigen-backend/alerts/anomaly_engine.py
"""
Motor de Detección Avanzada de Anomalías

Utiliza el FuzzyEngineV3 como base y agrega lógica determinista para 
clasificar patrones complejos en niveles: INFO, WARNING, CRITICAL.
Genera títulos y descripciones ricas para las alertas.
"""
from typing import Any, Dict, List, Optional
import logging

from analytics.fuzzy_engine import get_fuzzy_engine
from models.database import AlertLevel

logger = logging.getLogger("sigegen.anomaly_engine")


def detect_anomalies(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Analiza una lectura de telemetría y detecta anomalías.
    
    Args:
        data: Diccionario con la lectura del generador.
        
    Returns:
        Lista de diccionarios con la información de las alertas detectadas.
        Cada dict contiene: level, title, description, fuzzy_level.
    """
    alerts = []
    
    # 1. Ejecutar el motor fuzzy para obtener el nivel general y las contribuciones
    fuzzy_engine = get_fuzzy_engine()
    fuzzy_level, _, contrib = fuzzy_engine.evaluate(data)
    
    # Extraer valores reales para condiciones deterministas
    temp = float(data.get('temp_motor_c', 65) or 65)
    presion = float(data.get('presion_aceite_psi', 40) or 40)
    volt = float(data.get('voltaje_v', 220) or 220)
    freq = float(data.get('frecuencia_hz', 50) or 50)
    comb = float(data.get('combustible_pct', 50) or 50)
    horas = float(data.get('horas_motor', 0) or 0)
    
    # 2. Casos Específicos (Patrones Complejos)
    
    # Caso 1: Temperatura alta + Presión baja -> Riesgo de sobrecalentamiento crítico
    if temp > 90 and presion < 25:
        alerts.append({
            "level": AlertLevel.CRITICAL.value,
            "title": "Riesgo crítico de sobrecalentamiento",
            "description": f"Temperatura elevada ({temp:.1f}°C) combinada con baja presión de aceite ({presion:.1f} PSI). Apagado inminente recomendado.",
            "fuzzy_level": fuzzy_level
        })
    elif temp > 85 and presion < 30:
        alerts.append({
            "level": AlertLevel.WARNING.value,
            "title": "Advertencia de lubricación y temperatura",
            "description": f"Temperatura en aumento ({temp:.1f}°C) y presión de aceite límite ({presion:.1f} PSI).",
            "fuzzy_level": fuzzy_level
        })
        
    # Caso 2: Frecuencia inestable + Voltaje fuera de rango -> Posible problema de regulación
    freq_unstable = freq < 49.0 or freq > 51.0
    volt_bad = volt < 205 or volt > 235
    
    if freq_unstable and volt_bad:
        alerts.append({
            "level": AlertLevel.WARNING.value,
            "title": "Problema de regulación AVR/Gobernador",
            "description": f"Voltaje ({volt:.1f}V) y frecuencia ({freq:.1f}Hz) fuera de rangos nominales simultáneamente.",
            "fuzzy_level": fuzzy_level
        })
        
    # Caso 3: Combustible bajo + Muchas horas de operación -> Riesgo operativo
    if comb < 20 and horas > 3000:
        alerts.append({
            "level": AlertLevel.WARNING.value,
            "title": "Riesgo operativo alto",
            "description": f"Equipo con alto desgaste ({horas:.0f}h) operando con bajo nivel de combustible ({comb:.1f}%). Mayor probabilidad de cavitación.",
            "fuzzy_level": fuzzy_level
        })

    # Caso 4: Evaluaciones directas si no cayeron en patrones combinados pero son críticas
    if not alerts:
        if fuzzy_level >= 75:
            # Encontrar el mayor contribuyente
            if contrib:
                max_var = max(contrib.items(), key=lambda x: x[1])
                cause = max_var[0]
            else:
                cause = "múltiples factores"
                
            alerts.append({
                "level": AlertLevel.CRITICAL.value,
                "title": "Evaluación Fuzzy Crítica",
                "description": f"El sistema de inferencia difusa determinó un riesgo crítico. Principal contribuyente: {cause}.",
                "fuzzy_level": fuzzy_level
            })
        elif fuzzy_level >= 45:
             alerts.append({
                "level": AlertLevel.WARNING.value,
                "title": "Advertencia General de Operación",
                "description": f"Múltiples sensores indican operación subóptima (Score difuso: {fuzzy_level}).",
                "fuzzy_level": fuzzy_level
            })
            
    # Alarma por combustible muy bajo (independiente)
    if comb < 10 and not any("combustible" in a["title"].lower() for a in alerts):
        alerts.append({
            "level": AlertLevel.CRITICAL.value,
            "title": "Reserva de combustible crítica",
            "description": f"Nivel de combustible al {comb:.1f}%. Reabastecimiento urgente requerido.",
            "fuzzy_level": fuzzy_level
        })

    return alerts
