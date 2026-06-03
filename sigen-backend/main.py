import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import sqlite3
import os
import json
from typing import List, Dict, Any

# Añadir directorio raíz al path para importar el sistema difuso
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from sigegen_fuzzy_alerts import FuzzyAlertSystem
    fuzzy_system = FuzzyAlertSystem()
except Exception as e:
    print(f"Error cargando sistema difuso: {e}")
    fuzzy_system = None

app = FastAPI(title="SIGEGEN API", version="2.0.0")

# Permitir CORS para desarrollo local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Habilitamos todos los orígenes en desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta a la base de datos SQLite en la raíz del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "sigegen.db")

def get_db_connection():
    """Crea una conexión a la base de datos SQLite y retorna un cursor de diccionario."""
    if not os.path.exists(DB_PATH):
        raise HTTPException(
            status_code=500,
            detail=f"Base de datos no encontrada en {DB_PATH}. Corra el simulador primero para generarla."
        )
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def parse_row(row: sqlite3.Row) -> Dict[str, Any]:
    """Convierte una fila de SQLite a un diccionario de Python compatible con JSON."""
    d = dict(row)
    # Parsear alarmas si viene como string JSON
    if "alarmas" in d and d["alarmas"]:
        try:
            d["alarmas"] = json.loads(d["alarmas"])
        except Exception:
            d["alarmas"] = []

    # Evaluar con lógica difusa para obtener las contribuciones dinámicas en tiempo real
    contribuciones = {}
    if fuzzy_system:
        try:
            nivel, categoria, contrib = fuzzy_system.evaluate(d)
            d["alerta_difusa_nivel"] = nivel
            d["alerta_difusa_categoria"] = categoria
            contribuciones = contrib
        except Exception as ex:
            print(f"Error evaluando fila difusa: {ex}")
    d["alerta_difusa_contribuciones"] = contribuciones

    # Calcular colores de contribución para el frontend
    contrib_colores = {}
    for k, val in contribuciones.items():
        v_f = float(val) if val is not None else 0.0
        if v_f > 75.0:
            contrib_colores[k] = "#EF4444"
        elif v_f > 40.0:
            contrib_colores[k] = "#F97316"
        else:
            contrib_colores[k] = "#10B981"
    d["alerta_difusa_contribuciones_colores"] = contrib_colores

    # Calcular color del combustible
    comb = d.get("combustible_pct", 50.0)
    comb = float(comb) if comb is not None else 50.0
    if comb > 50.0:
        d["fuel_color"] = "#10B981"
    elif comb > 20.0:
        d["fuel_color"] = "#F59E0B"
    else:
        d["fuel_color"] = "#EF4444"

    # Calcular color del estado de alerta
    alerta_lvl = d.get("alerta_difusa_nivel", 0.0)
    alerta_lvl = float(alerta_lvl) if alerta_lvl is not None else 0.0
    if alerta_lvl > 75.0:
        d["alert_color"] = "#EF4444"
    elif alerta_lvl > 35.0:
        d["alert_color"] = "#F97316"
    else:
        d["alert_color"] = "#10B981"

    return d

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "SIGEGEN API funcionando correctamente",
        "database_path": DB_PATH,
        "exists": os.path.exists(DB_PATH)
    }

@app.get("/api/generadores")
def get_generadores():
    """Retorna la lista de todos los generadores con su último estado y telemetría."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Consulta para obtener la lectura más reciente de cada nodo_id
        query = """
            SELECT l1.* FROM lecturas l1
            INNER JOIN (
                SELECT nodo_id, MAX(timestamp) as max_ts
                FROM lecturas
                GROUP BY nodo_id
            ) l2 ON l1.nodo_id = l2.nodo_id AND l1.timestamp = l2.max_ts
            ORDER BY l1.nodo_id
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        resultado = []
        for r in rows:
            parsed = parse_row(r)
            # Agregar campos amigables para el frontend
            parsed["id"] = parsed["nodo_id"]
            parsed["nombre"] = f"Generador {parsed['nodo_id'].split('_')[1]}"
            resultado.append(parsed)
            
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/telemetria/{generador_id}/ultimo")
def get_ultima_lectura(generador_id: str):
    """Retorna la última lectura de telemetría de un generador específico."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM lecturas WHERE nodo_id = ? ORDER BY timestamp DESC LIMIT 1",
            (generador_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(
                status_code=404, 
                detail=f"No se encontraron lecturas para el generador '{generador_id}'"
            )
            
        parsed = parse_row(row)
        parsed["id"] = parsed["nodo_id"]
        parsed["nombre"] = f"Generador {parsed['nodo_id'].split('_')[1]}"
        return parsed
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/telemetria/{generador_id}/historial")
def get_historial_lecturas(generador_id: str, limite: int = 20):
    """Retorna las últimas N lecturas de un generador, ordenadas cronológicamente."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Subconsulta para obtener las últimas lecturas y luego ordenarlas ascendentemente para graficar
        query = """
            SELECT * FROM (
                SELECT * FROM lecturas 
                WHERE nodo_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ) ORDER BY timestamp ASC
        """
        cursor.execute(query, (generador_id, limite))
        rows = cursor.fetchall()
        conn.close()
        
        resultado = []
        for r in rows:
            parsed = parse_row(r)
            parsed["id"] = parsed["nodo_id"]
            parsed["nombre"] = f"Generador {parsed['nodo_id'].split('_')[1]}"
            resultado.append(parsed)
            
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/alertas")
def get_alertas_recientes(limite: int = 50):
    """Retorna las lecturas con nivel de alerta difuso alto (>= 35) o alarmas activas."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT * FROM lecturas 
            WHERE alerta_difusa_nivel >= 35 OR estado != 'normal'
            ORDER BY timestamp DESC 
            LIMIT ?
        """
        cursor.execute(query, (limite,))
        rows = cursor.fetchall()
        conn.close()
        
        resultado = []
        for r in rows:
            parsed = parse_row(r)
            parsed["id"] = parsed["nodo_id"]
            parsed["nombre"] = f"Generador {parsed['nodo_id'].split('_')[1]}"
            resultado.append(parsed)
            
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/resumen")
def get_resumen_global():
    """Retorna un resumen del estado de todos los generadores para el dashboard."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener última lectura de todos los generadores
        query = """
            SELECT l1.estado, l1.alerta_difusa_nivel, l1.combustible_pct, l1.encendido 
            FROM lecturas l1
            INNER JOIN (
                SELECT nodo_id, MAX(timestamp) as max_ts
                FROM lecturas
                GROUP BY nodo_id
            ) l2 ON l1.nodo_id = l2.nodo_id AND l1.timestamp = l2.max_ts
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        total = len(rows)
        if total == 0:
            return {
                "total": 0,
                "encendidos": 0,
                "apagados": 0,
                "normal": 0,
                "alerta": 0,
                "falla": 0,
                "alerta_promedio": 0.0,
                "combustible_promedio": 0.0
            }
            
        encendidos = sum(1 for r in rows if r["encendido"])
        normal = sum(1 for r in rows if r["estado"] == "normal")
        alerta = sum(1 for r in rows if r["estado"] == "alerta")
        falla = sum(1 for r in rows if r["estado"] == "falla")
        alerta_promedio = sum(r["alerta_difusa_nivel"] for r in rows) / total
        combustible_promedio = sum(r["combustible_pct"] for r in rows) / total
        
        return {
            "total": total,
            "encendidos": encendidos,
            "apagados": total - encendidos,
            "normal": normal,
            "alerta": alerta,
            "falla": falla,
            "alerta_promedio": round(alerta_promedio, 1),
            "combustible_promedio": round(combustible_promedio, 1)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
