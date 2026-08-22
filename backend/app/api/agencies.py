from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.models import Agency, User
from backend.app.api.auth import get_current_user
from backend.app.schemas.schemas import AgencyResponse
from typing import List

router = APIRouter(prefix="/agencies", tags=["Agency Profiling"])

@router.get("/", response_model=List[AgencyResponse])
def get_agencies(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    agencies = db.query(Agency).all()
    return agencies

@router.get("/{id}/risk", response_model=AgencyResponse)
def get_agency_risk_profile(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    agency = db.query(Agency).filter(Agency.id == id).first()
    if not agency:
        raise HTTPException(status_code=404, detail="Implementing Agency not found")
    return agency

@router.get("/{id}/controlled-backtrack")
def get_agency_controlled_backtrack(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from backend.app.services.backtracking import perform_agency_controlled_backtrack
    res = perform_agency_controlled_backtrack(db, id)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res
