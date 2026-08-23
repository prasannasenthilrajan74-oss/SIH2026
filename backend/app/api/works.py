from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.models import Work, RiskScore, Payment, Document, User
from backend.app.api.auth import get_current_user, apply_role_filters
from backend.app.schemas.schemas import WorkResponse, RiskScoreResponse, PaymentResponse, DocumentResponse
from backend.app.nlp.similarity import find_duplicate_works
from typing import List, Dict, Any, Optional

def resolve_work_backtracking(db: Session, w: Work, agency_cache: dict, district_cache: dict, threshold: float = 30.0, fast_mode: bool = False):
    rs = w.risk_scores
    primary_attribution = "NORMAL_CASE"
    backtrack_summary = "This project's risk level is within normal parameters."
    
    if rs and rs.overall_score >= threshold:
        primary_attribution = "ISOLATED_CASE"
        backtrack_summary = "This project shows isolated risk indicators, but no broader organizational or geographic concentration pattern exists."
        
        ag_counts = agency_cache.get("_ag_counts", {})
        ds_counts = district_cache.get("_ds_counts", {})
        
        ag_c = ag_counts.get(w.implementing_agency_id, 0)
        ds_c = ds_counts.get(w.district_code, 0)
        
        if w.implementing_agency_id and ag_c >= 55:
            primary_attribution = "AGENCY_CONCENTRATION"
            agency_name = w.implementing_agency.name if w.implementing_agency else f"Agency #{w.implementing_agency_id}"
            backtrack_summary = f"Agency concentration: {ag_c} elevated risk projects concentrated under {agency_name}."
        elif w.district_code and ds_c >= 50:
            primary_attribution = "DISTRICT_CONCENTRATION"
            backtrack_summary = f"District concentration: {ds_c} elevated risk projects concentrated in district {w.district_code}."
                
    return primary_attribution, backtrack_summary

router = APIRouter(prefix="/works", tags=["Projects"])

@router.get("/", response_model=Dict[str, Any])
def get_works(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    state: Optional[str] = None,
    district: Optional[str] = None,
    constituency: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    risk_level: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(20, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    query = db.query(Work).join(RiskScore)
    
    # 1. Apply global role filters
    query = apply_role_filters(query, Work, current_user)

    # 2. Apply query filters
    if state:
        query = query.filter(Work.state_code == state)
    if district:
        query = query.filter(Work.district_code == district)
    if constituency:
        query = query.filter(Work.constituency == constituency)
    if category:
        query = query.filter(Work.category == category)
    if status:
        query = query.filter(Work.status == status)
        
    if risk_level:
        if risk_level == "CRITICAL":
            query = query.filter(RiskScore.overall_score >= 85.0)
        elif risk_level == "HIGH":
            query = query.filter(RiskScore.overall_score >= 70.0, RiskScore.overall_score < 85.0)
        elif risk_level == "MEDIUM":
            query = query.filter(RiskScore.overall_score >= 45.0, RiskScore.overall_score < 70.0)
        elif risk_level == "LOW":
            query = query.filter(RiskScore.overall_score < 45.0)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Work.id.like(search_filter)) | 
            (Work.description.like(search_filter)) |
            (Work.mp_name.like(search_filter)) |
            (Work.constituency.like(search_filter))
        )

    total = query.count()
    
    # Default sorting: Overall Risk Score descending (Priority Queue)
    query = query.order_by(RiskScore.overall_score.desc())
    
    works = query.offset(offset).limit(limit).all()

    # Format output
    work_list = []
    from sqlalchemy import func
    ag_rows = db.query(Work.implementing_agency_id, func.count(Work.id))\
        .join(RiskScore)\
        .filter(RiskScore.overall_score >= 35.0, Work.implementing_agency_id.isnot(None))\
        .group_by(Work.implementing_agency_id)\
        .all()
    agency_cache = {"_ag_counts": dict(ag_rows)}

    ds_rows = db.query(Work.district_code, func.count(Work.id))\
        .join(RiskScore)\
        .filter(RiskScore.overall_score >= 35.0, Work.district_code.isnot(None))\
        .group_by(Work.district_code)\
        .all()
    district_cache = {"_ds_counts": dict(ds_rows)}

    for w in works:
        agency_name = w.implementing_agency.name if w.implementing_agency else None
        
        # Format RiskScoreResponse
        rs = w.risk_scores
        rs_resp = None
        if rs:
            rs_resp = RiskScoreResponse(
                work_id=rs.work_id,
                overall_score=rs.overall_score,
                financial_risk=rs.financial_risk,
                delay_risk=rs.delay_risk,
                cost_risk=rs.cost_risk,
                duplicate_risk=rs.duplicate_risk,
                payment_risk=rs.payment_risk,
                compliance_risk=rs.compliance_risk,
                document_risk=rs.document_risk,
                geographic_risk=rs.geographic_risk,
                factors=rs.factors,
                updated_at=rs.updated_at
            )
            
        attr, summary = resolve_work_backtracking(db, w, agency_cache, district_cache, fast_mode=True)
            
        work_list.append(WorkResponse(
            id=w.id,
            description=w.description,
            category=w.category,
            work_type=w.work_type,
            mp_name=w.mp_name,
            constituency=w.constituency,
            state_code=w.state_code,
            district_code=w.district_code,
            block=w.block,
            village=w.village,
            latitude=w.latitude,
            longitude=w.longitude,
            recommendation_date=w.recommendation_date,
            sanction_date=w.sanction_date,
            expected_completion_date=w.expected_completion_date,
            actual_completion_date=w.actual_completion_date,
            status=w.status,
            implementing_agency_id=w.implementing_agency_id,
            estimated_cost=w.estimated_cost,
            sanctioned_amount=w.sanctioned_amount,
            expenditure=w.expenditure,
            physical_progress=w.physical_progress,
            financial_progress=w.financial_progress,
            created_at=w.created_at,
            implementing_agency_name=agency_name,
            risk_scores=rs_resp,
            primary_attribution=attr,
            backtrack_summary=summary
        ))

    return {
        "total": total,
        "works": work_list
    }

@router.get("/{id}", response_model=WorkResponse)
def get_work_by_id(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    w = db.query(Work).filter(Work.id == id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Project not found")
        
    agency_name = w.implementing_agency.name if w.implementing_agency else None
    
    rs = w.risk_scores
    rs_resp = None
    if rs:
        rs_resp = RiskScoreResponse(
            work_id=rs.work_id,
            overall_score=rs.overall_score,
            financial_risk=rs.financial_risk,
            delay_risk=rs.delay_risk,
            cost_risk=rs.cost_risk,
            duplicate_risk=rs.duplicate_risk,
            payment_risk=rs.payment_risk,
            compliance_risk=rs.compliance_risk,
            document_risk=rs.document_risk,
            geographic_risk=rs.geographic_risk,
            factors=rs.factors,
            updated_at=rs.updated_at
        )

    attr, summary = resolve_work_backtracking(db, w, {}, {})

    return WorkResponse(
        id=w.id,
        description=w.description,
        category=w.category,
        work_type=w.work_type,
        mp_name=w.mp_name,
        constituency=w.constituency,
        state_code=w.state_code,
        district_code=w.district_code,
        block=w.block,
        village=w.village,
        latitude=w.latitude,
        longitude=w.longitude,
        recommendation_date=w.recommendation_date,
        sanction_date=w.sanction_date,
        expected_completion_date=w.expected_completion_date,
        actual_completion_date=w.actual_completion_date,
        status=w.status,
        implementing_agency_id=w.implementing_agency_id,
        estimated_cost=w.estimated_cost,
        sanctioned_amount=w.sanctioned_amount,
        expenditure=w.expenditure,
        physical_progress=w.physical_progress,
        financial_progress=w.financial_progress,
        created_at=w.created_at,
        implementing_agency_name=agency_name,
        risk_scores=rs_resp,
        primary_attribution=attr,
        backtrack_summary=summary
    )

@router.get("/{id}/payments", response_model=List[PaymentResponse])
def get_work_payments(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    payments = db.query(Payment).filter(Payment.work_id == id).order_by(Payment.payment_date.asc()).all()
    return payments

@router.get("/{id}/documents", response_model=List[DocumentResponse])
def get_work_documents(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    documents = db.query(Document).filter(Document.work_id == id).order_by(Document.upload_date.desc()).all()
    return documents

@router.get("/{id}/similar", response_model=List[Dict[str, Any]])
def get_work_similar_duplicates(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    work = db.query(Work).filter(Work.id == id).first()
    if not work:
        raise HTTPException(status_code=404, detail="Project not found")
    duplicates = find_duplicate_works(db, work, threshold=0.6)
    return duplicates

@router.get("/{id}/controlled-backtrack")
def get_work_controlled_backtrack(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from backend.app.services.backtracking import backtrack_work_root_cause
    res = backtrack_work_root_cause(db, id)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res

@router.post("/refresh-scores")
def refresh_all_risk_scores(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Recalculate risk scores for all works. Ministry Admin and Investigation Officers only."""
    if current_user.role.name not in ["Ministry Administrator", "Investigation Officer"]:
        raise HTTPException(status_code=403, detail="Only Ministry Administrators and Investigation Officers can trigger score refresh.")
    from backend.app.services.risk import update_all_risk_scores
    try:
        update_all_risk_scores(db)
        total = db.query(Work).count()
        return {"refreshed": total, "total": total, "message": f"AI risk scores refreshed for {total} projects."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Score refresh failed: {str(e)}")


