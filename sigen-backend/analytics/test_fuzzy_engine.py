# sigen-backend/analytics/test_fuzzy_engine.py
"""
Tests unitarios para el motor de lógica difusa v3.0 de SIGEGEN.
Valida todas las reglas de inferencia y rangos de salida.
"""
import unittest
from analytics.fuzzy_engine import FuzzyEngineV3


class TestFuzzyEngineV3(unittest.TestCase):
    """Tests del motor de inferencia difusa."""

    @classmethod
    def setUpClass(cls):
        """Inicializar el motor fuzzy una sola vez."""
        cls.engine = FuzzyEngineV3()

    def test_all_normal_low_risk(self):
        """R6: Todas las variables normales → riesgo bajo."""
        data = {
            "temp_motor_c": 65, "presion_aceite_psi": 40,
            "voltaje_v": 220, "frecuencia_hz": 50,
            "combustible_pct": 60, "horas_motor": 500,
            "rpm": 1500, "vibracion_mms": 3,
        }
        nivel, clasificacion, _ = self.engine.evaluate(data)
        self.assertLess(nivel, 35, "Todas normales debería dar riesgo bajo")
        self.assertEqual(clasificacion, "INFO")

    def test_critical_temperature(self):
        """R4: Temperatura crítica → riesgo crítico."""
        data = {
            "temp_motor_c": 120, "presion_aceite_psi": 40,
            "voltaje_v": 220, "frecuencia_hz": 50,
            "combustible_pct": 60, "horas_motor": 500,
            "rpm": 1500, "vibracion_mms": 3,
        }
        nivel, clasificacion, contrib = self.engine.evaluate(data)
        self.assertGreater(nivel, 50, "Temp crítica debería elevar riesgo")
        self.assertIn(clasificacion, ["WARNING", "CRITICAL"])
        self.assertGreater(contrib.get("temperatura", 0), 50)

    def test_high_temp_low_pressure(self):
        """R1/R5: Temperatura alta + Presión baja → riesgo alto/crítico."""
        data = {
            "temp_motor_c": 100, "presion_aceite_psi": 12,
            "voltaje_v": 220, "frecuencia_hz": 50,
            "combustible_pct": 60, "horas_motor": 500,
            "rpm": 1500, "vibracion_mms": 3,
        }
        nivel, clasificacion, contrib = self.engine.evaluate(data)
        self.assertGreater(nivel, 45, "Temp alta + presión baja → alto riesgo")
        self.assertGreater(contrib.get("presion_aceite", 0), 0)

    def test_unstable_frequency_bad_voltage(self):
        """R2: Frecuencia inestable + Voltaje fuera de rango → riesgo alto."""
        data = {
            "temp_motor_c": 65, "presion_aceite_psi": 40,
            "voltaje_v": 195, "frecuencia_hz": 47,
            "combustible_pct": 60, "horas_motor": 500,
            "rpm": 1500, "vibracion_mms": 3,
        }
        nivel, clasificacion, _ = self.engine.evaluate(data)
        self.assertGreater(nivel, 35, "Freq inestable + voltaje bajo → riesgo")

    def test_low_fuel_high_hours(self):
        """R3/R15: Combustible bajo + Horas altas → riesgo alto."""
        data = {
            "temp_motor_c": 65, "presion_aceite_psi": 40,
            "voltaje_v": 220, "frecuencia_hz": 50,
            "combustible_pct": 8, "horas_motor": 4000,
            "rpm": 1500, "vibracion_mms": 3,
        }
        nivel, clasificacion, contrib = self.engine.evaluate(data)
        self.assertGreater(nivel, 35, "Combustible bajo + horas altas → riesgo")
        self.assertGreater(contrib.get("combustible", 0), 0)

    def test_critical_vibration(self):
        """R12: Vibración crítica → riesgo crítico."""
        data = {
            "temp_motor_c": 65, "presion_aceite_psi": 40,
            "voltaje_v": 220, "frecuencia_hz": 50,
            "combustible_pct": 60, "horas_motor": 500,
            "rpm": 1500, "vibracion_mms": 16,
        }
        nivel, clasificacion, _ = self.engine.evaluate(data)
        self.assertGreater(nivel, 50, "Vibración crítica → riesgo alto")

    def test_risk_levels_classification(self):
        """Verificar que la clasificación respeta los umbrales."""
        engine = self.engine

        # Datos normales
        data_low = {
            "temp_motor_c": 65, "presion_aceite_psi": 40,
            "voltaje_v": 220, "frecuencia_hz": 50,
            "combustible_pct": 80, "horas_motor": 200,
            "rpm": 1500, "vibracion_mms": 2,
        }
        nivel, clasificacion, _ = engine.evaluate(data_low)
        self.assertEqual(clasificacion, "INFO", f"Nivel {nivel} debería ser INFO")

    def test_contributions_all_keys_present(self):
        """Verificar que las contribuciones contienen todas las claves."""
        data = {
            "temp_motor_c": 65, "presion_aceite_psi": 40,
            "voltaje_v": 220, "frecuencia_hz": 50,
            "combustible_pct": 50, "horas_motor": 500,
            "rpm": 1500, "vibracion_mms": 3,
        }
        _, _, contrib = self.engine.evaluate(data)
        expected_keys = {"temperatura", "presion_aceite", "voltaje", "frecuencia",
                         "combustible", "rpm", "horas_operacion"}
        self.assertEqual(set(contrib.keys()), expected_keys)

    def test_missing_values_use_defaults(self):
        """Verificar que datos incompletos no causan error."""
        data = {"temp_motor_c": 80}  # Faltan todas las demás
        nivel, clasificacion, _ = self.engine.evaluate(data)
        self.assertIsInstance(nivel, float)
        self.assertIn(clasificacion, ["INFO", "WARNING", "CRITICAL"])

    def test_overload_condition(self):
        """R10: Voltaje alto + Frecuencia alta → riesgo alto (sobrecarga)."""
        data = {
            "temp_motor_c": 65, "presion_aceite_psi": 40,
            "voltaje_v": 248, "frecuencia_hz": 53,
            "combustible_pct": 60, "horas_motor": 500,
            "rpm": 1500, "vibracion_mms": 3,
        }
        nivel, _, _ = self.engine.evaluate(data)
        self.assertGreater(nivel, 35, "Sobrecarga → riesgo elevado")


if __name__ == "__main__":
    unittest.main()
