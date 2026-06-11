# sigen-backend/routers/alerts_router.py
"""Endpoints para Alertas."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from pydantic import BaseModel

from models.database import get_session, Alert
from auth.service import get_current_active_user, User
from alerts.manager import get_alerts, resolve_alert, mark_alert_read

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

class ResolveRequest(BaseModel):
    alert_id: int

@router.get("/", response_model=List[Alert])
async def list_alerts(
    node_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    return get_alerts(session, node_id, status, limit)

@router.post("/resolve", response_model=Alert)
async def api_resolve_alert(
    req: ResolveRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    alert = resolve_alert(session, req.alert_id, current_user.username)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.post("/read/{alert_id}", response_model=Alert)
async def api_mark_read(
    alert_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    alert = mark_alert_read(session, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert
