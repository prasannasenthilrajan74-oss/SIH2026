from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.models import Rule, User
from backend.app.api.auth import get_current_user
from backend.app.schemas.schemas import RuleResponse, RuleUpdateRequest
from backend.app.services.risk import update_all_risk_scores
from typing import List

router = APIRouter(prefix="/rules", tags=["Rule Engine Configuration"])

@router.get("/", response_model=List[RuleResponse])
def get_rules(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rules = db.query(Rule).all()
    return rules

@router.put("/{id}", response_model=RuleResponse)
def update_rule(
    id: str,
    request: RuleUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Security: only Ministry Admins can update system rules
    if current_user.role.name != "Ministry Administrator":
        raise HTTPException(status_code=403, detail="Only Ministry Administrators can update detection rules.")
        
    rule = db.query(Rule).filter(Rule.id == id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    # Update fields
    if request.name is not None:
        rule.name = request.name
    if request.description is not None:
        rule.description = request.description
    if request.severity is not None:
        rule.severity = request.severity
    if request.condition_expression is not None:
        rule.condition_expression = request.condition_expression
    if request.threshold is not None:
        rule.threshold = request.threshold
    if request.enabled is not None:
        rule.enabled = request.enabled

    db.commit()
    db.refresh(rule)
    return rule

@router.post("/evaluate")
def trigger_rules_evaluation(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Re-run rule engine and re-score everything
    from backend.app.rules.engine import run_rules_on_work
    from backend.app.models.models import Work
    
    works = db.query(Work).all()
    for w in works:
        run_rules_on_work(db, w)
        
    # Recalculate risk scores
    update_all_risk_scores(db)
    
    return {"message": "Successfully executed rules engine and updated risk scoring profiles across all projects."}
