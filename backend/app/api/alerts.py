from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.models import Alert, Work, User
from backend.app.api.auth import get_current_user, apply_role_filters
from backend.app.schemas.schemas import AlertResponse, AlertStatusUpdate
from typing import List

router = APIRouter(prefix="/alerts", tags=["Alert Monitoring"])

@router.get("/", response_model=List[AlertResponse])
def get_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    severity: str = None,
    status: str = "ACTIVE"
):
    query = db.query(Alert).join(Work)
    
    # Apply global role filters
    query = apply_role_filters(query, Work, current_user)
    
    if severity:
        query = query.filter(Alert.severity == severity)
    if status:
        query = query.filter(Alert.status == status)
        
    alerts = query.order_by(Alert.created_at.desc()).all()
    
    response = []
    for a in alerts:
        response.append(AlertResponse(
            id=a.id,
            work_id=a.work_id,
            alert_type=a.alert_type,
            severity=a.severity,
            score=a.score,
            reason=a.reason,
            evidence=a.evidence,
            status=a.status,
            created_at=a.created_at,
            work_description=a.work.description
        ))
        
    return response

@router.put("/{id}/status", response_model=AlertResponse)
def update_alert_status(
    id: int,
    request: AlertStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = db.query(Alert).filter(Alert.id == id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert.status = request.status
    db.commit()
    db.refresh(alert)
    
    return AlertResponse(
        id=alert.id,
        work_id=alert.work_id,
        alert_type=alert.alert_type,
        severity=alert.severity,
        score=alert.score,
        reason=alert.reason,
        evidence=alert.evidence,
        status=alert.status,
        created_at=alert.created_at,
        work_description=alert.work.description
    )
