from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.db.session import get_db
from backend.app.api.auth import get_current_user, apply_role_filters
from backend.app.models.models import User, Work, RiskScore, Alert, State, District, Agency
from typing import Dict, Any, List

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/overview", response_model=Dict[str, Any])
def get_dashboard_overview(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 1. Base counts
    works_q = db.query(Work)
    works_q = apply_role_filters(works_q, Work, current_user)
    
    total_works = works_q.count()
    
    # Financial metrics
    fin_metrics = works_q.with_entities(
        func.sum(Work.sanctioned_amount).label("total_sanctioned"),
        func.sum(Work.expenditure).label("total_expenditure")
    ).first()
    
    total_sanctioned = float(fin_metrics.total_sanctioned or 0.0)
    total_expenditure = float(fin_metrics.total_expenditure or 0.0)

    # Status counts
    completed_works = works_q.filter(Work.status == "Completed").count()
    ongoing_works = works_q.filter(Work.status == "Ongoing").count()
    sanctioned_works = works_q.filter(Work.status == "Sanctioned").count()

    # Risk metrics (join RiskScore)
    risk_q = db.query(Work).join(RiskScore)
    risk_q = apply_role_filters(risk_q, Work, current_user)
    
    high_risk_works = risk_q.filter(RiskScore.overall_score >= 70.0).count()
    critical_risk_works = risk_q.filter(RiskScore.overall_score >= 85.0).count()

    # Delayed projects count (overdue based on expected completion date)
    import datetime
    today = datetime.date.today()
    delayed_works = works_q.filter(
        Work.status != "Completed",
        Work.expected_completion_date < today
    ).count()

    # Alert counts
    alert_q = db.query(Alert).join(Work)
    alert_q = apply_role_filters(alert_q, Work, current_user)
    
    total_alerts = alert_q.filter(Alert.status == "ACTIVE").count()
    critical_alerts = alert_q.filter(Alert.severity == "CRITICAL", Alert.status == "ACTIVE").count()
    duplicate_alerts = alert_q.filter(Alert.alert_type == "DUP_WORK", Alert.status == "ACTIVE").count()
    cost_alerts = alert_q.filter(Alert.alert_type == "RULE_COST_OVERRUN", Alert.status == "ACTIVE").count()
    doc_alerts = alert_q.filter(Alert.alert_type == "RULE_DOC_MISMATCH", Alert.status == "ACTIVE").count()

    # Category breakdown
    cat_q = works_q.with_entities(
        Work.category,
        func.count(Work.id).label("count"),
        func.sum(Work.sanctioned_amount).label("sanctioned"),
        func.sum(Work.expenditure).label("expenditure")
    ).group_by(Work.category).all()
    
    category_breakdown = [
        {
            "category": cat,
            "count": count,
            "sanctioned_amount": float(sanc or 0.0),
            "expenditure": float(exp or 0.0)
        } for cat, count, sanc, exp in cat_q
    ]

    # State rankings (National scope or local)
    state_rankings = []
    if current_user.role.name in ["Ministry Administrator", "Investigation Officer"]:
        state_q = db.query(
            State.name,
            func.avg(RiskScore.overall_score).label("avg_risk"),
            func.count(Work.id).label("project_count")
        ).select_from(Work).join(RiskScore).join(State, Work.state_code == State.code).group_by(State.name).order_by(func.avg(RiskScore.overall_score).desc()).all()
        
        state_rankings = [
            {"state_name": name, "avg_risk_score": float(risk or 0.0), "project_count": count}
            for name, risk, count in state_q
        ]

    # District rankings
    dist_q = db.query(
        District.name,
        func.avg(RiskScore.overall_score).label("avg_risk"),
        func.count(Work.id).label("project_count")
    ).select_from(Work).join(RiskScore).join(District, Work.district_code == District.code)
    
    # If state nodal, restrict to state districts
    if current_user.role.name == "State Nodal Authority":
        dist_q = dist_q.filter(Work.state_code == current_user.state)
        
    dist_results = dist_q.group_by(District.name).order_by(func.avg(RiskScore.overall_score).desc()).limit(10).all()
    district_rankings = [
        {"district_name": name, "avg_risk_score": float(risk or 0.0), "project_count": count}
        for name, risk, count in dist_results
    ]

    # Top high-risk agencies
    agency_q = db.query(
        Agency.name,
        Agency.risk_score,
        func.count(Work.id).label("project_count")
    ).select_from(Work).join(Agency, Work.implementing_agency_id == Agency.id)
    
    if current_user.role.name == "State Nodal Authority":
        agency_q = agency_q.filter(Work.state_code == current_user.state)
    elif current_user.role.name == "District Authority":
        agency_q = agency_q.filter(Work.district_code == current_user.district)
        
    agency_results = agency_q.group_by(Agency.name, Agency.risk_score).order_by(Agency.risk_score.desc()).limit(5).all()
    agency_rankings = [
        {"agency_name": name, "risk_score": float(score or 0.0), "project_count": count}
        for name, score, count in agency_results
    ]

    return {
        "total_works": total_works,
        "total_sanctioned_amount": total_sanctioned,
        "total_expenditure": total_expenditure,
        "completed_works": completed_works,
        "ongoing_works": ongoing_works,
        "sanctioned_works": sanctioned_works,
        "delayed_works": delayed_works,
        "high_risk_works": high_risk_works,
        "critical_risk_works": critical_risk_works,
        "total_alerts": total_alerts,
        "critical_alerts": critical_alerts,
        "duplicate_alerts": duplicate_alerts,
        "cost_alerts": cost_alerts,
        "doc_alerts": doc_alerts,
        "category_breakdown": category_breakdown,
        "state_rankings": state_rankings,
        "district_rankings": district_rankings,
        "agency_rankings": agency_rankings
    }

@router.get("/heatmap", response_model=List[Dict[str, Any]])
def get_heatmap_coordinates(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Retrieve works with coordinates and their risk scores
    q = db.query(
        Work.id, Work.description, Work.latitude, Work.longitude, RiskScore.overall_score, Work.status
    ).join(RiskScore).filter(Work.latitude.isnot(None), Work.longitude.isnot(None))
    
    q = apply_role_filters(q, Work, current_user)
    results = q.all()
    
    return [
        {
            "work_id": wid,
            "description": desc,
            "latitude": lat,
            "longitude": lon,
            "risk_score": float(score),
            "status": status
        } for wid, desc, lat, lon, score, status in results
    ]
