from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.models import Investigation, InvestigationAction, Work, User
from backend.app.api.auth import get_current_user, apply_role_filters
from backend.app.schemas.schemas import InvestigationResponse, InvestigationCreate, InvestigationUpdate, InvestigationActionResponse
from typing import List
import datetime

router = APIRouter(prefix="/investigations", tags=["Case Management"])

@router.get("/", response_model=List[InvestigationResponse])
def get_investigations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: str = None
):
    query = db.query(Investigation).join(Work)
    
    # Apply global role filters
    query = apply_role_filters(query, Work, current_user)
    
    if status:
        query = query.filter(Investigation.status == status)
        
    cases = query.order_by(Investigation.created_at.desc()).all()
    
    response = []
    for c in cases:
        actions_resp = []
        for act in c.actions:
            actions_resp.append(InvestigationActionResponse(
                id=act.id,
                investigation_id=act.investigation_id,
                performed_by_name=act.performed_by_user.username if hasattr(act, 'performed_by_user') and act.performed_by_user else db.query(User).filter(User.id == act.performed_by).first().username,
                action=act.action,
                notes=act.notes,
                timestamp=act.timestamp
            ))
            
        response.append(InvestigationResponse(
            id=c.id,
            work_id=c.work_id,
            work_description=c.work.description,
            assigned_to_id=c.assigned_to,
            assigned_to_name=c.assigned_officer.username if c.assigned_officer else None,
            priority=c.priority,
            status=c.status,
            findings=c.findings,
            action_taken=c.action_taken,
            resolution_state=c.resolution_state,
            created_at=c.created_at,
            resolved_at=c.resolved_at,
            actions=actions_resp
        ))
        
    return response

@router.post("/", response_model=InvestigationResponse)
def create_investigation(
    request: InvestigationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify work exists
    work = db.query(Work).filter(Work.id == request.work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check if investigation already active for this work
    existing = db.query(Investigation).filter(
        Investigation.work_id == request.work_id,
        Investigation.status != "Resolved"
    ).first()
    if existing:
         raise HTTPException(status_code=400, detail="Active investigation case already exists for this project.")

    case = Investigation(
        work_id=request.work_id,
        assigned_to=request.assigned_to,
        priority=request.priority,
        status="Detected"
    )
    db.add(case)
    db.commit()
    db.refresh(case)

    # Log action
    act = InvestigationAction(
        investigation_id=case.id,
        performed_by=current_user.id,
        action="Case Detected & Opened",
        notes=f"Investigation initiated. Severity level: {request.priority}."
    )
    db.add(act)
    db.commit()

    return InvestigationResponse(
        id=case.id,
        work_id=case.work_id,
        work_description=work.description,
        assigned_to_id=case.assigned_to,
        assigned_to_name=db.query(User).filter(User.id == case.assigned_to).first().username if case.assigned_to else None,
        priority=case.priority,
        status=case.status,
        findings=case.findings,
        action_taken=case.action_taken,
        resolution_state=case.resolution_state,
        created_at=case.created_at,
        actions=[]
    )

@router.put("/{id}", response_model=InvestigationResponse)
def update_investigation(
    id: int,
    request: InvestigationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    case = db.query(Investigation).filter(Investigation.id == id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Investigation case not found")

    notes_log = []
    
    if request.status is not None and request.status != case.status:
        notes_log.append(f"Status changed from {case.status} to {request.status}")
        case.status = request.status
        if request.status == "Resolved":
            case.resolved_at = datetime.datetime.utcnow()

    if request.assigned_to is not None and request.assigned_to != case.assigned_to:
        officer = db.query(User).filter(User.id == request.assigned_to).first()
        officer_name = officer.username if officer else "None"
        notes_log.append(f"Assigned officer updated to: {officer_name}")
        case.assigned_to = request.assigned_to

    if request.findings is not None:
        case.findings = request.findings
        notes_log.append("Findings updated")

    if request.action_taken is not None:
        case.action_taken = request.action_taken
        notes_log.append("Action taken details updated")

    if request.resolution_state is not None:
        case.resolution_state = request.resolution_state
        notes_log.append(f"Resolution state defined as: {request.resolution_state}")

    db.commit()
    db.refresh(case)

    # Log action to audit trail
    if notes_log:
        act = InvestigationAction(
            investigation_id=case.id,
            performed_by=current_user.id,
            action="Case Update",
            notes="; ".join(notes_log)
        )
        db.add(act)
        db.commit()

    # Re-fetch actions
    actions_resp = []
    for act in case.actions:
        actions_resp.append(InvestigationActionResponse(
            id=act.id,
            investigation_id=act.investigation_id,
            performed_by_name=db.query(User).filter(User.id == act.performed_by).first().username,
            action=act.action,
            notes=act.notes,
            timestamp=act.timestamp
        ))

    return InvestigationResponse(
        id=case.id,
        work_id=case.work_id,
        work_description=case.work.description,
        assigned_to_id=case.assigned_to,
        assigned_to_name=case.assigned_officer.username if case.assigned_officer else None,
        priority=case.priority,
        status=case.status,
        findings=case.findings,
        action_taken=case.action_taken,
        resolution_state=case.resolution_state,
        created_at=case.created_at,
        resolved_at=case.resolved_at,
        actions=actions_resp
    )
