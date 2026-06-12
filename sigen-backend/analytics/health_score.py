# sigen-backend/analytics/health_score.py
"""
Sistema de Health Score para SIGEGEN v3.0

Calcula un índice de salud (0-100) para cada grupo electrógeno basado
en la ponderación de múltiples variables de telemetría.

Rangos:
  90-100  → Excelente (verde)
  70-89   → Bueno (azul)
  50-69   → Advertencia (amarillo)
   0-49   → Crítico (rojo)

Pesos:
  Temperatura      → 20%
  Presión aceite   → 15%
  Voltaje          → 20%
  Frecuencia       → 15%
  Horas motor      → 15%
  Combustible      → 15%
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Tuple

logger = logging.getLogger("sigegen.health_score")


# ── Rangos ideales y límites ─────────────────────────────────

IDEAL_RANGES = {
    "temp_motor_c":      {"min": 60, "max": 85, "critical_low": 20, "critical_high": 110},
    "presion_aceite_psi": {"min": 25, "max": 65, "critical_low": 10, "critical_high": 80},
    "voltaje_v":         {"min": 215, "max": 228, "critical_low": 190, "critical_high": 250},
    "frecuencia_hz":     {"min": 49.5, "max": 50.5, "critical_low": 47, "critical_high": 53},
    "horas_motor":       {"max_ideal": 2000, "critical": 5000},
    "combustible_pct":   {"min_ideal": 30, "critical": 10},
}

WEIGHTS = {
    "temp_motor_c": 0.20,
    "presion_aceite_psi": 0.15,
    "voltaje_v": 0.20,
    "frecuencia_hz": 0.15,
    "horas_motor": 0.15,
    "combustible_pct": 0.15,
}


def _score_range_variable(value: float, ideal_min: float, ideal_max: float,
                           critical_low: float, critical_high: float) -> float:
    """
    Calcula score 0-100 para una variable con rango ideal.
    100 = dentro del rango ideal
    0   = en o más allá de los límites críticos
    """
    if ideal_min <= value <= ideal_max:
        return 100.0

    if value < ideal_min:
        if value <= critical_low:
            return 0.0
        # Escala lineal entre critical_low e ideal_min
        return max(0.0, (value - critical_low) / (ideal_min - critical_low) * 100.0)

    # value > ideal_max
    if value >= critical_high:
        return 0.0
    return max(0.0, (critical_high - value) / (critical_high - ideal_max) * 100.0)


def _score_combustible(value: float) -> float:
    """Score de combustible: 100 al tener >30%, 0 al tener <10%."""
    if value >= 30.0:
        return 100.0
    if value <= 10.0:
        return 0.0
    return (value - 10.0) / 20.0 * 100.0


def _score_horas(value: float) -> float:
    """Score de horas de motor: penaliza equipos con muchas horas sin mantenimiento."""
    if value <= 2000:
        return 100.0
    if value >= 5000:
        return 20.0  # No baja a 0 porque puede seguir funcionando
    return 100.0 - (value - 2000) / 3000 * 80.0


def calculate_health_score(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcula el Health Score de un grupo electrógeno.

    Args:
        data: Diccionario con las lecturas de telemetría del generador.

    Returns:
        Diccionario con:
            - score: float (0-100)
            - category: str (excelente/bueno/advertencia/critico)
            - category_color: str (hex color)
            - breakdown: dict con score individual por variable
    """
    breakdown = {}

    # Temperatura
    temp = float(data.get("temp_motor_c", 65) or 65)
    r = IDEAL_RANGES["temp_motor_c"]
    breakdown["temp_motor_c"] = round(
        _score_range_variable(temp, r["min"], r["max"], r["critical_low"], r["critical_high"]), 1
    )

    # Presión de aceite
    presion = float(data.get("presion_aceite_psi", 40) or 40)
    r = IDEAL_RANGES["presion_aceite_psi"]
    breakdown["presion_aceite_psi"] = round(
        _score_range_variable(presion, r["min"], r["max"], r["critical_low"], r["critical_high"]), 1
    )

    # Voltaje
    voltaje = float(data.get("voltaje_v", 220) or 220)
    r = IDEAL_RANGES["voltaje_v"]
    breakdown["voltaje_v"] = round(
        _score_range_variable(voltaje, r["min"], r["max"], r["critical_low"], r["critical_high"]), 1
    )

    # Frecuencia
    freq = float(data.get("frecuencia_hz", 50) or 50)
    r = IDEAL_RANGES["frecuencia_hz"]
    breakdown["frecuencia_hz"] = round(
        _score_range_variable(freq, r["min"], r["max"], r["critical_low"], r["critical_high"]), 1
    )

    # Horas de motor
    horas = float(data.get("horas_motor", 0) or 0)
    breakdown["horas_motor"] = round(_score_horas(horas), 1)

    # Combustible
    comb = float(data.get("combustible_pct", 50) or 50)
    breakdown["combustible_pct"] = round(_score_combustible(comb), 1)

    # Score ponderado final
    score = sum(
        breakdown[key] * WEIGHTS[key]
        for key in WEIGHTS
    )
    score = round(min(100.0, max(0.0, score)), 1)

    # Categoría
    if score >= 90:
        category = "excelente"
        category_color = "#10B981"
    elif score >= 70:
        category = "bueno"
        category_color = "#3B82F6"
    elif score >= 50:
        category = "advertencia"
        category_color = "#F59E0B"
    else:
        category = "critico"
        category_color = "#EF4444"

    return {
        "score": score,
        "category": category,
        "category_color": category_color,
        "breakdown": breakdown,
    }
