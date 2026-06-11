# sigen-backend/routers/maintenance.py
"""Endpoints para Mantenimiento y Predicciones."""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel

from models.database import get_session, MaintenanceRecord
from auth.service import get_current_active_user, get_current_admin_user, User
from analytics.predictive_maintenance import calculate_predictions

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])

class MaintenanceCreate(BaseModel):
    node_id: str
    tecnico: str
    tipo: str
    descripcion: str = ""
    repuestos: str = ""
    horas_equipo: float
    costo: float = 0.0
    observaciones: str = ""

@router.post("/", response_model=MaintenanceRecord)
async def create_maintenance(
    record_in: MaintenanceCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    record = MaintenanceRecord(**record_in.model_dump())
    session.add(record)
    session.commit()
    session.refresh(record)
    return record

@router.get("/node/{node_id}", response_model=List[MaintenanceRecord])
async def get_node_maintenance(
    node_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    statement = select(MaintenanceRecord).where(
        MaintenanceRecord.node_id == node_id
    ).order_by(MaintenanceRecord.fecha.desc())
    return session.exec(statement).all()

@router.get("/predictions/{node_id}", response_model=List[Dict[str, Any]])
async def get_node_predictions(
    node_id: str,
    horas_actuales: float,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    return calculate_predictions(session, node_id, horas_actuales)
