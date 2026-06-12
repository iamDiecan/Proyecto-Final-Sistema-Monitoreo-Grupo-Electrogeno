# sigen-backend/routers/kpi.py
"""Endpoints para consultar KPIs operativos."""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from models.database import get_session, MaintenanceRecord, Alert
from auth.service import get_current_active_user, User

router = APIRouter(prefix="/api/kpi", tags=["kpi"])

@router.get("/", response_model=Dict[str, Any])
async def get_kpis(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    from main import get_resumen_global
    try:
        resumen = get_resumen_global()
    except Exception:
        resumen = {"encendidos": 0, "total": 0, "combustible_promedio": 0}

    total = resumen.get("total", 0)
    encendidos = resumen.get("encendidos", 0)
    falla = resumen.get("falla", 0)
    
    # Cálculo derivado
    disponibilidad = 100.0 if total == 0 else ((total - falla) / total) * 100.0
    mtbf = 1200 + (encendidos * 5) # Simulado inteligente
    mttr = 2.5 # Mock para reparar fallas
    consumo = resumen.get("combustible_promedio", 0)

    return {
        "disponibilidad": round(disponibilidad, 1),
        "disponibilidad_trend": "+0.1",
        "mtbf_horas": round(mtbf, 0),
        "mtbf_trend": "+12",
        "mttr_horas": mttr,
        "mttr_trend": "-0.1",
        "consumo_promedio_lh": round(consumo, 1),
        "consumo_trend": "-0.2",
    }
