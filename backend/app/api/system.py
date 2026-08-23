from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.models import (
    Role, User, State, District, Agency, Work, Payment,
    Rule, RiskScore, Document, Investigation, InvestigationAction,
    Alert, SystemSetting
)
from backend.app.api.auth import get_current_user
from datetime import date, datetime

router = APIRouter(prefix="/system", tags=["System Utilities"])

@router.get("/stats")
def get_system_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns system health stats: DB record counts, alert counts, last score refresh."""
    total_works = db.query(Work).count()
    total_alerts = db.query(Alert).filter(Alert.status == "ACTIVE").count()
    critical_alerts = db.query(Alert).filter(Alert.severity == "CRITICAL", Alert.status == "ACTIVE").count()
    total_investigations = db.query(Investigation).count()
    risk_score_count = db.query(RiskScore).count()

    # Last risk score update time
    last_score = db.query(RiskScore).order_by(RiskScore.updated_at.desc()).first()
    last_refresh = last_score.updated_at.isoformat() if last_score and last_score.updated_at else None

    # ML model status — we consider it "ready" if at least 80% of works have scores
    ml_coverage = round((risk_score_count / total_works * 100), 1) if total_works > 0 else 0
    ml_status = "Operational" if ml_coverage >= 80 else ("Partial" if ml_coverage > 0 else "Offline")

    return {
        "total_works": total_works,
        "risk_scores_computed": risk_score_count,
        "ml_coverage_pct": ml_coverage,
        "ml_status": ml_status,
        "active_alerts": total_alerts,
        "critical_alerts": critical_alerts,
        "open_investigations": total_investigations,
        "last_score_refresh": last_refresh,
        "db_status": "Connected"
    }

def sqla_to_dict(obj):
    if obj is None:
        return None
    d = {}
    for column in obj.__table__.columns:
        val = getattr(obj, column.name)
        if isinstance(val, (date, datetime)):
            d[column.name] = val.isoformat()
        else:
            d[column.name] = val
    return d

@router.get("/download-db")
def download_database_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only Ministry Administrator and State Nodal Authority are authorized to export the database
    if current_user.role.name not in ["Ministry Administrator", "State Nodal Authority"]:
        raise HTTPException(
            status_code=403,
            detail="Only Ministry Administrators and State Nodal Authorities are authorized to download database backups."
        )

    # Compile data from all tables
    data = {
        "roles": [sqla_to_dict(x) for x in db.query(Role).all()],
        "users": [
            {k: v for k, v in sqla_to_dict(x).items() if k != "hashed_password"}
            for x in db.query(User).all()
        ],
        "states": [sqla_to_dict(x) for x in db.query(State).all()],
        "districts": [sqla_to_dict(x) for x in db.query(District).all()],
        "agencies": [sqla_to_dict(x) for x in db.query(Agency).all()],
        "works": [sqla_to_dict(x) for x in db.query(Work).all()],
        "payments": [sqla_to_dict(x) for x in db.query(Payment).all()],
        "rules": [sqla_to_dict(x) for x in db.query(Rule).all()],
        "risk_scores": [sqla_to_dict(x) for x in db.query(RiskScore).all()],
        "documents": [sqla_to_dict(x) for x in db.query(Document).all()],
        "investigations": [sqla_to_dict(x) for x in db.query(Investigation).all()],
        "investigation_actions": [sqla_to_dict(x) for x in db.query(InvestigationAction).all()],
        "alerts": [sqla_to_dict(x) for x in db.query(Alert).all()],
        "system_settings": [sqla_to_dict(x) for x in db.query(SystemSetting).all()],
    }

    headers = {
        "Content-Disposition": "attachment; filename=mplads_sentinel_backup.json"
    }
    return JSONResponse(content=data, headers=headers)
