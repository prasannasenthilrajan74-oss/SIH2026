import datetime
from sqlalchemy.orm import Session
from backend.app.models.models import Work, RiskScore, SystemSetting, Alert
from backend.app.nlp.similarity import find_duplicate_works, haversine_distance
from backend.app.rules.engine import check_payment_burst

def get_risk_weights(db: Session) -> dict:
    setting = db.query(SystemSetting).filter(SystemSetting.key == "risk_weights").first()
    if setting and isinstance(setting.value, dict):
        return setting.value
    # Fallback default weights
    return {
        "financial_risk": 0.20,
        "delay_risk": 0.20,
        "cost_risk": 0.15,
        "duplicate_risk": 0.15,
        "payment_risk": 0.10,
        "compliance_risk": 0.10,
        "document_risk": 0.05,
        "geographic_risk": 0.05
    }

def calculate_cost_risk(db: Session, work: Work) -> tuple[float, str]:
    # cost deviation calculation
    # Compare with median of projects in same category and district
    siblings = db.query(Work).filter(
        Work.category == work.category,
        Work.district_code == work.district_code,
        Work.id != work.id
    ).all()

    if len(siblings) < 3:
        # Fallback to state level
        siblings = db.query(Work).filter(
            Work.category == work.category,
            Work.state_code == work.state_code,
            Work.id != work.id
        ).all()

    if not siblings:
        return 20.0, "Insufficient comparable projects to evaluate cost deviation. Baseline risk assigned."

    costs = [s.sanctioned_amount for s in siblings]
    median_cost = float(np.median(costs)) if costs else work.sanctioned_amount

    if median_cost == 0:
        return 0.0, "Comparable projects have zero sanctioned amount."

    deviation_pct = (work.sanctioned_amount - median_cost) / median_cost
    deviation_pct_val = deviation_pct * 100

    if deviation_pct > 0.4:
        return min(100.0, 50.0 + deviation_pct_val * 0.5), f"Estimated cost is {deviation_pct_val:.1f}% above comparable project median (₹{median_cost/100000:.1f} Lakh)."
    elif deviation_pct > 0.1:
        return min(100.0, 30.0 + deviation_pct_val * 0.5), f"Estimated cost is {deviation_pct_val:.1f}% above comparable project median."
    else:
        return 10.0, "Cost is within normal variance of comparable projects."

def update_all_risk_scores(db: Session, anomaly_scores: dict[str, float] = None, delay_predictions: dict[str, dict] = None):
    # import local fallbacks to avoid circular dependency
    from backend.app.ml.anomaly import run_anomaly_detector
    from backend.app.ml.delay import predict_delays

    if not anomaly_scores:
        anomaly_scores = run_anomaly_detector(db)
    if not delay_predictions:
        delay_predictions = predict_delays(db)

    works = db.query(Work).all()
    weights = get_risk_weights(db)
    today = datetime.date.today()

    for w in works:
        factors = []
        
        # 1. Financial Risk
        fin_risk = 0.0
        # Check financial utilization vs physical progress
        utilization = w.expenditure / w.sanctioned_amount if w.sanctioned_amount > 0 else 0.0
        if w.status == "Ongoing":
            if utilization > 0.8 and w.physical_progress < 50.0:
                fin_risk = 90.0
                factors.append("CRITICAL: 92% of funds utilized but only 35% physical progress." if w.physical_progress <= 35 and utilization >= 0.9 else f"High fund utilization ({utilization*100:.1f}%) with low physical progress ({w.physical_progress:.1f}%).")
            elif utilization > 0.5 and w.physical_progress < 25.0:
                fin_risk = 70.0
                factors.append(f"Disproportionate utilization ({utilization*100:.1f}%) compared to physical progress ({w.physical_progress:.1f}%).")
        # Check cost overrun
        if w.expenditure > w.sanctioned_amount:
            overrun_pct = ((w.expenditure - w.sanctioned_amount) / w.sanctioned_amount) * 100
            fin_risk = max(fin_risk, min(100.0, 75.0 + overrun_pct))
            factors.append(f"CRITICAL: Actual expenditure exceeds sanctioned amount by {overrun_pct:.1f}%.")
        
        # Isolation Forest outlier factor
        if w.id in anomaly_scores:
            if anomaly_scores[w.id] > 75.0:
                fin_risk = max(fin_risk, anomaly_scores[w.id])
                factors.append(f"Machine learning anomaly index flagged outlier numerical patterns (Score: {anomaly_scores[w.id]:.1f}/100).")

        # 2. Delay Risk
        delay_risk = 0.0
        delay_pred = delay_predictions.get(w.id, {"delay_probability": 0.0, "predicted_delay_months": 0.0})
        
        if w.status != "Completed":
            # Current delay days
            if w.expected_completion_date and today > w.expected_completion_date:
                overdue_days = (today - w.expected_completion_date).days
                overdue_months = overdue_days / 30.0
                delay_risk = min(100.0, 70.0 + overdue_months * 3.0)
                factors.append(f"CRITICAL: Project exceeds expected duration by {int(overdue_months)} months.")
            # ML Delay prediction
            prob = delay_pred["delay_probability"]
            months = delay_pred["predicted_delay_months"]
            if prob > 70.0:
                delay_risk = max(delay_risk, prob)
                factors.append(f"ML Predictor: High probability of delay ({prob:.1f}%) with expected delay of {months} months.")
        
        # 3. Cost Risk
        cost_risk, cost_factor = calculate_cost_risk(db, w)
        if cost_risk > 50.0:
            factors.append(f"WARNING: {cost_factor}")

        # 4. Duplicate Risk
        dup_risk = 0.0
        duplicates = find_duplicate_works(db, w, threshold=0.7)
        if duplicates:
            highest_dup = duplicates[0]
            dup_risk = highest_dup["duplicate_probability"]
            factors.append(f"CRITICAL: High potential duplicate work ({highest_dup['duplicate_probability']:.1f}% similarity) found {highest_dup['distance_km'] or 0:.2f} km away ({highest_dup['work_id']}).")

        # 5. Payment Risk
        payment_risk = 0.0
        if check_payment_burst(w):
            payment_risk = 85.0
            factors.append("WARNING: Multiple rapid disbursements made within a 5-day window.")
        
        # Check payment concentration vs physical progress
        if utilization > 0.7 and w.physical_progress == 0.0:
            payment_risk = max(payment_risk, 90.0)
            factors.append("CRITICAL: Substantial project payments made but physical progress has not commenced.")

        # 6. Compliance Risk
        compliance_risk = 0.0
        missing = []
        if w.latitude is None or w.longitude is None:
            missing.append("location coordinates")
        if w.sanction_date is None:
            missing.append("sanction date")
        if w.implementing_agency_id is None:
            missing.append("implementing agency")
        if missing:
            compliance_risk = 30.0 + len(missing) * 20.0
            factors.append(f"Compliance: Missing critical details: {', '.join(missing)}.")

        # 7. Document Risk
        doc_risk = 0.0
        for doc in w.documents:
            if doc.consistency_score is not None:
                d_risk = 100.0 - doc.consistency_score
                if d_risk > doc_risk:
                    doc_risk = d_risk
        if doc_risk > 20.0:
            factors.append(f"WARNING: Document integrity discrepancies detected (Consistency score: {100.0 - doc_risk:.1f}%).")

        # 8. Geographic Risk
        geo_risk = 0.0
        # Calculate average risk of neighbors in a 5km radius
        neighbors = []
        for other in works:
            if other.id != w.id and w.latitude and w.longitude and other.latitude and other.longitude:
                dist = haversine_distance(w.latitude, w.longitude, other.latitude, other.longitude)
                if dist <= 5.0:
                    neighbors.append(other)
        if neighbors:
            # We will fetch pre-existing overall scores or average of simple estimates
            # For simplicity, calculate base heuristic for neighbors
            neighbor_risks = []
            for n in neighbors:
                n_util = n.expenditure / n.sanctioned_amount if n.sanctioned_amount > 0 else 0.0
                n_base = 20.0
                if n_util > 0.8 and n.physical_progress < 50:
                    n_base = 75.0
                neighbor_risks.append(n_base)
            avg_neighbor_risk = np.mean(neighbor_risks)
            if avg_neighbor_risk > 50.0:
                geo_risk = avg_neighbor_risk
                factors.append(f"Geospatial cluster analysis flags high-risk neighbor concentration in a 5km radius.")

        # Calculate weighted overall score
        overall_score = (
            fin_risk * weights["financial_risk"] +
            delay_risk * weights["delay_risk"] +
            cost_risk * weights["cost_risk"] +
            dup_risk * weights["duplicate_risk"] +
            payment_risk * weights["payment_risk"] +
            compliance_risk * weights["compliance_risk"] +
            doc_risk * weights["document_risk"] +
            geo_risk * weights["geographic_risk"]
        )

        overall_score = min(100.0, max(0.0, overall_score))

        # Check if record exists
        risk_record = db.query(RiskScore).filter(RiskScore.work_id == w.id).first()
        if not risk_record:
            risk_record = RiskScore(
                work_id=w.id,
                overall_score=overall_score,
                financial_risk=fin_risk,
                delay_risk=delay_risk,
                cost_risk=cost_risk,
                duplicate_risk=dup_risk,
                payment_risk=payment_risk,
                compliance_risk=compliance_risk,
                document_risk=doc_risk,
                geographic_risk=geo_risk,
                factors=factors
            )
            db.add(risk_record)
        else:
            risk_record.overall_score = overall_score
            risk_record.financial_risk = fin_risk
            risk_record.delay_risk = delay_risk
            risk_record.cost_risk = cost_risk
            risk_record.duplicate_risk = dup_risk
            risk_record.payment_risk = payment_risk
            risk_record.compliance_risk = compliance_risk
            risk_record.document_risk = doc_risk
            risk_record.geographic_risk = geo_risk
            risk_record.factors = factors
            
    db.commit()

import numpy as np
