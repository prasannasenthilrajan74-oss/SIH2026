from sqlalchemy.orm import Session
from backend.app.models.models import Work, RiskScore, Agency, District, State
from typing import Dict, Any, Optional

def perform_agency_controlled_backtrack(db: Session, agency_id: int, threshold: float = 30.0) -> Dict[str, Any]:
    agency = db.query(Agency).filter(Agency.id == agency_id).first()
    if not agency:
        return {"error": f"Agency with ID {agency_id} not found."}

    agency_works = db.query(Work).filter(Work.implementing_agency_id == agency.id).all()
    if not agency_works:
        return {
            "agency_id": agency.id,
            "agency_name": agency.name,
            "risk_concentration_level": "INSUFFICIENT_DATA",
            "attribution_summary": "No active project portfolio found for this agency to perform controlled baseline analysis.",
            "recommendation": "Maintain standard monitoring."
        }

    # Extract controlled variables
    dist_codes = list(set(w.district_code for w in agency_works if w.district_code))
    cat_names = list(set(w.category for w in agency_works if w.category))

    # Peer group: Same district & category, different agency
    peer_works = db.query(Work).filter(
        Work.district_code.in_(dist_codes),
        Work.category.in_(cat_names),
        Work.implementing_agency_id != agency.id
    ).all()

    agency_flagged = [w for w in agency_works if w.risk_scores and w.risk_scores.overall_score >= threshold]
    peer_flagged = [w for w in peer_works if w.risk_scores and w.risk_scores.overall_score >= threshold]

    agency_rate = (len(agency_flagged) / len(agency_works)) * 100.0 if agency_works else 0.0
    peer_rate = (len(peer_flagged) / len(peer_works)) * 100.0 if peer_works else 0.0

    if peer_rate > 0:
        multiplier = agency_rate / peer_rate
    elif agency_rate > 0:
        multiplier = 2.5
    else:
        multiplier = 1.0

    if multiplier >= 2.0 and agency_rate >= 15.0:
        concentration_level = "HIGH"
        attribution = f"Difference persists after controlling for district and category. Agency anomaly rate ({agency_rate:.1f}%) is {multiplier:.2f}x higher than peer baseline ({peer_rate:.1f}%). Concentration is uniquely attributable to the agency."
        recommendation = "Initiate detailed audit review of agency's full project portfolio."
    elif multiplier >= 1.3 and agency_rate >= 10.0:
        concentration_level = "MODERATE"
        attribution = f"Moderate elevation detected ({agency_rate:.1f}% vs {peer_rate:.1f}% peer average, {multiplier:.2f}x ratio) holding district and category constant."
        recommendation = "Request periodic status updates and execution timeline verification."
    else:
        concentration_level = "NORMAL"
        attribution = f"Agency performance ({agency_rate:.1f}% anomaly rate) is within expected variance of peer baseline ({peer_rate:.1f}%)."
        recommendation = "No concentrated agency-level risk detected."

    return {
        "agency_id": agency.id,
        "agency_name": agency.name,
        "district_code": agency.district_code,
        "risk_concentration_level": concentration_level,
        "controlled_comparison": {
            "agency_anomaly_rate": round(agency_rate, 1),
            "agency_flagged_count": len(agency_flagged),
            "agency_total_projects": len(agency_works),
            "peer_baseline_rate": round(peer_rate, 1),
            "peer_sample_size": len(peer_works),
            "multiplier_ratio": round(multiplier, 2),
            "variables_controlled": ["district_code", "category"]
        },
        "attribution_summary": attribution,
        "recommendation": recommendation
    }

def perform_district_controlled_backtrack(db: Session, district_code: str, threshold: float = 30.0) -> Dict[str, Any]:
    district = db.query(District).filter(District.code == district_code).first()
    if not district:
        return {"error": f"District with code {district_code} not found."}

    dist_works = db.query(Work).filter(Work.district_code == district_code).all()
    if not dist_works:
        return {
            "district_code": district_code,
            "district_name": district.name,
            "risk_concentration_level": "INSUFFICIENT_DATA",
            "attribution_summary": "No active projects found in this district."
        }

    cat_names = list(set(w.category for w in dist_works if w.category))
    
    # Peer group: Same state & category, different district
    peer_dist_works = db.query(Work).filter(
        Work.state_code == district.state_code,
        Work.category.in_(cat_names),
        Work.district_code != district_code
    ).all()

    dist_flagged = [w for w in dist_works if w.risk_scores and w.risk_scores.overall_score >= threshold]
    peer_flagged = [w for w in peer_dist_works if w.risk_scores and w.risk_scores.overall_score >= threshold]

    dist_rate = (len(dist_flagged) / len(dist_works)) * 100.0 if dist_works else 0.0
    peer_rate = (len(peer_flagged) / len(peer_dist_works)) * 100.0 if peer_dist_works else 0.0

    multiplier = (dist_rate / peer_rate) if peer_rate > 0 else (2.0 if dist_rate > 0 else 1.0)

    if multiplier >= 1.8 and dist_rate >= 15.0:
        concentration_level = "HIGH"
        attribution = f"District anomaly rate ({dist_rate:.1f}%) is {multiplier:.2f}x state peer baseline ({peer_rate:.1f}%), controlling for state and category. Points to systemic local admin or verification gaps."
    elif multiplier >= 1.25 and dist_rate >= 10.0:
        concentration_level = "MODERATE"
        attribution = f"District anomaly rate ({dist_rate:.1f}%) shows moderate elevation over state peer baseline ({peer_rate:.1f}%)."
    else:
        concentration_level = "NORMAL"
        attribution = f"District performance ({dist_rate:.1f}%) is aligned with state baseline ({peer_rate:.1f}%)."

    return {
        "district_code": district.code,
        "district_name": district.name,
        "state_code": district.state_code,
        "risk_concentration_level": concentration_level,
        "controlled_comparison": {
            "district_anomaly_rate": round(dist_rate, 1),
            "district_flagged_count": len(dist_flagged),
            "district_total_projects": len(dist_works),
            "state_peer_rate": round(peer_rate, 1),
            "state_peer_sample_size": len(peer_dist_works),
            "multiplier_ratio": round(multiplier, 2),
            "variables_controlled": ["state_code", "category"]
        },
        "attribution_summary": attribution
    }

def backtrack_work_root_cause(db: Session, work_id: str, threshold: float = 30.0) -> Dict[str, Any]:
    work = db.query(Work).filter(Work.id == work_id).first()
    if not work:
        return {"error": f"Work ID {work_id} not found."}

    rs = work.risk_scores
    is_anomalous = rs and rs.overall_score >= threshold

    agency_analysis = None
    district_analysis = None
    primary_attribution = "ISOLATED_CASE"
    summary = "This project shows isolated risk indicators, but no broader organizational or geographic concentration pattern exists."

    if work.implementing_agency_id:
        agency_analysis = perform_agency_controlled_backtrack(db, work.implementing_agency_id, threshold=threshold)
        if agency_analysis.get("risk_concentration_level") in ["HIGH", "MODERATE"]:
            primary_attribution = "AGENCY_CONCENTRATION"
            summary = f"Root Cause Attribution: High risk concentration identified at Implementing Agency level ({agency_analysis['agency_name']}). Anomaly rate is {agency_analysis['controlled_comparison']['multiplier_ratio']}x higher than peer baseline in same district & category."

    if primary_attribution == "ISOLATED_CASE" and work.district_code:
        district_analysis = perform_district_controlled_backtrack(db, work.district_code, threshold=threshold)
        if district_analysis.get("risk_concentration_level") in ["HIGH", "MODERATE"]:
            primary_attribution = "DISTRICT_CONCENTRATION"
            summary = f"Root Cause Attribution: Geographic risk concentration identified at District level ({district_analysis['district_name']}). Anomaly rate is {district_analysis['controlled_comparison']['multiplier_ratio']}x higher than state baseline."

    return {
        "work_id": work.id,
        "description": work.description,
        "risk_score": rs.overall_score if rs else 0.0,
        "is_flagged_anomalous": is_anomalous,
        "primary_attribution": primary_attribution,
        "summary": summary,
        "agency_controlled_analysis": agency_analysis,
        "district_controlled_analysis": district_analysis
    }
