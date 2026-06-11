# sigen-backend/routers/health.py
"""Endpoints para consultar el Health Score."""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from auth.service import get_current_active_user, User
from analytics.health_score import calculate_health_score
import influx_client
import sqlite3
import os
from config import get_settings

router = APIRouter(prefix="/api/health", tags=["health"])

@router.get("/{node_id}", response_model=Dict[str, Any])
async def get_node_health(
    node_id: str,
    current_user: User = Depends(get_current_active_user)
):
    # Intentar obtener de InfluxDB
    data = None
    try:
        if influx_client.check_connection():
            data = influx_client.get_last_reading(node_id)
    except Exception:
        pass
        
    # Fallback a SQLite
    if not data:
        settings = get_settings()
        if os.path.exists(settings.sqlite_db_path):
            conn = sqlite3.connect(settings.sqlite_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM lecturas WHERE nodo_id = ? ORDER BY timestamp DESC LIMIT 1", (node_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                data = dict(row)
                
    if not data:
        # Default de gracia si el nodo no tiene datos aún
        data = {
            "temp_motor_c": 0, "presion_aceite_psi": 0, "voltaje_v": 0, 
            "frecuencia_hz": 0, "horas_motor": 0, "combustible_pct": 0
        }
        
    return calculate_health_score(data)
