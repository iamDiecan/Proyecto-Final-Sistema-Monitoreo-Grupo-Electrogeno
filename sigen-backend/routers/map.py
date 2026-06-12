# sigen-backend/routers/map.py
"""Endpoints para el mapa geográfico."""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from models.database import get_session, NodeConfig
from auth.service import get_current_active_user, User

router = APIRouter(prefix="/api/map", tags=["map"])

@router.get("/nodes", response_model=List[Dict[str, Any]])
async def get_map_nodes(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    from main import get_generadores
    try:
        live_data = get_generadores()
        live_map = {n["id"]: n for n in live_data}
    except Exception:
        live_map = {}

    nodes = session.exec(select(NodeConfig)).all()
    result = []
    for n in nodes:
        live = live_map.get(n.node_id, {})
        estado = live.get("estado", "normal")
        # Health score simple derivado del estado para el mapa
        health = 95.0 if estado == "normal" else (70.0 if estado == "precaucion" else (40.0 if estado == "alerta" else 10.0))
        
        result.append({
            "node_id": n.node_id,
            "nombre": n.nombre,
            "lat": n.lat,
            "lon": n.lon,
            "zona": n.zona,
            "estado": estado,
            "health_score": live.get("health_score", health)
        })
    return result
