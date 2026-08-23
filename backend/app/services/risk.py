import datetime
import numpy as np
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

def calculate_cost_risk(db: Session, work: Work, category_medians: dict = None) -> tuple[float, str]:
    # cost deviation calculation
    median_cost = None
    if category_medians and (work.category, work.district_code) in category_medians:
        median_cost = category_medians[(work.category, work.district_code)]
    else:
        # Fallback to query
        siblings = db.query(Work).filter(
            Work.category == work.category,
            Work.district_code == work.district_code,
            Work.id != work.id
        ).all()
        if not siblings:
            siblings = db.query(Work).filter(
                Work.category == work.category,
                Work.state_code == work.state_code,
                Work.id != work.id
            ).all()
        if siblings:
            costs = [s.sanctioned_amount for s in siblings]
            median_cost = float(np.median(costs)) if costs else work.sanctioned_amount

    if median_cost is None or median_cost == 0:
        return 10.0, "Cost is within normal variance of comparable projects."

    deviation_pct = (work.sanctioned_amount - median_cost) / median_cost
    deviation_pct_val = deviation_pct * 100

    if deviation_pct > 0.6:
        return min(92.5, 40.0 + deviation_pct_val * 0.4), f"Estimated cost is {deviation_pct_val:.1f}% above comparable project median (₹{median_cost/100000:.1f} Lakh)."
    elif deviation_pct > 0.35:
        return min(55.0, 20.0 + deviation_pct_val * 0.4), f"Estimated cost is {deviation_pct_val:.1f}% above comparable project median."
    else:
        return 10.0, "Cost is within normal variance of comparable projects."

def validate_factor_correlations(work: Work, factors: list[str]) -> list[str]:
    """
    STEP 5 Runtime Self-Check:
    Validates that cited numbers in reason strings match current project database fields.
    Suppresses stale/inconsistent factors and formats accurate dynamic explanations.
    """
    validated = []
    utilization_pct = (work.expenditure / work.sanctioned_amount * 100.0) if work.sanctioned_amount > 0 else 0.0
    phys_prog = work.physical_progress if work.physical_progress is not None else 0.0

    for factor in factors:
        # 1. Financial Progress / Utilization Mismatch Validation
        if "utiliz" in factor.lower() or "physical progress" in factor.lower():
            if work.status == "Completed":
                continue # Completed projects with 100% progress are normal
            gap = utilization_pct - phys_prog
            if utilization_pct < 60.0 or phys_prog >= 50.0 or gap < 25.0:
                continue # No longer satisfies mismatch anomaly criteria
            factor = f"High fund utilization ({utilization_pct:.1f}%) with lower physical progress ({phys_prog:.1f}%) (Gap: {gap:.1f}pts)."

        # 2. Cost Overrun Validation
        elif "expenditure exceeds" in factor.lower() or "overrun" in factor.lower():
            if work.expenditure <= work.sanctioned_amount:
                continue # No overrun
            overrun_pct = ((work.expenditure - work.sanctioned_amount) / work.sanctioned_amount) * 100.0
            factor = f"CRITICAL: Actual expenditure (₹{work.expenditure/100000:.2f} Lakh) exceeds sanctioned allocation (₹{work.sanctioned_amount/100000:.2f} Lakh) by {overrun_pct:.1f}%."

        # 3. Delay Validation
        elif "exceeds expected duration" in factor.lower() or "completion date" in factor.lower():
            if work.status == "Completed":
                continue # Completed works are not currently delaying
            today = datetime.date.today()
            if not work.expected_completion_date or today <= work.expected_completion_date:
                continue # Not overdue
            overdue_months = int((today - work.expected_completion_date).days / 30.0)
            if overdue_months < 1:
                continue
            factor = f"CRITICAL: Ongoing project exceeds expected completion date by {overdue_months} months."

        validated.append(factor)

    return list(dict.fromkeys(validated)) # Remove duplicate strings

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

    # Precompute cost medians per (category, district_code)
    cat_dist_costs = {}
    for w in works:
        if w.category and w.district_code and w.sanctioned_amount:
            cat_dist_costs.setdefault((w.category, w.district_code), []).append(w.sanctioned_amount)
    category_medians = {key: float(np.median(c_list)) for key, c_list in cat_dist_costs.items() if len(c_list) >= 2}
    existing_risks = {r.work_id: r for r in db.query(RiskScore).all()}
    existing_alerts = {(a.work_id, a.alert_type): a for a in db.query(Alert).filter(Alert.status == "ACTIVE").all()}

    for idx, w in enumerate(works, 1):
        factors = []
        phys_prog = w.physical_progress if w.physical_progress is not None else 0.0
        
        # 1. Financial Risk
        fin_risk = 0.0
        utilization_ratio = w.expenditure / w.sanctioned_amount if w.sanctioned_amount > 0 else 0.0
        utilization_pct = utilization_ratio * 100.0

        if w.status == "Ongoing":
            gap = utilization_pct - phys_prog
            if utilization_pct >= 80.0 and phys_prog < 50.0 and gap >= 30.0:
                fin_risk = 90.0
                factors.append(f"High fund utilization ({utilization_pct:.1f}%) with lower physical progress ({phys_prog:.1f}%) (Gap: {gap:.1f}pts).")
            elif utilization_pct >= 60.0 and phys_prog < 30.0 and gap >= 25.0:
                fin_risk = 70.0
                factors.append(f"Disproportionate utilization ({utilization_pct:.1f}%) compared to physical progress ({phys_prog:.1f}%).")
        
        # Check cost overrun
        if w.expenditure > w.sanctioned_amount:
            overrun_pct = ((w.expenditure - w.sanctioned_amount) / w.sanctioned_amount) * 100.0
            fin_risk = max(fin_risk, min(92.5, 75.0 + overrun_pct))
            factors.append(f"CRITICAL: Actual expenditure (₹{w.expenditure/100000:.2f} Lakh) exceeds sanctioned allocation (₹{w.sanctioned_amount/100000:.2f} Lakh) by {overrun_pct:.1f}%.")
        
        # Isolation Forest outlier factor
        if w.id in anomaly_scores:
            if anomaly_scores[w.id] > 80.0:
                fin_risk = max(fin_risk, min(92.5, anomaly_scores[w.id]))
                factors.append(f"Machine learning anomaly index flagged outlier numerical patterns (Score: {min(92.5, anomaly_scores[w.id]):.1f}/100).")

        # 2. Delay Risk
        delay_risk = 0.0
        delay_pred = delay_predictions.get(w.id, {"delay_probability": 0.0, "predicted_delay_months": 0.0})
        
        if w.status != "Completed":
            # Current delay days
            if w.expected_completion_date and today > w.expected_completion_date:
                overdue_days = (today - w.expected_completion_date).days
                overdue_months = overdue_days / 30.0
                delay_risk = min(92.5, 60.0 + overdue_months * 3.0)
                factors.append(f"CRITICAL: Ongoing project exceeds expected completion date by {int(overdue_months)} months.")
            # ML Delay prediction
            prob = min(92.5, delay_pred["delay_probability"])
            months = delay_pred["predicted_delay_months"]
            if prob > 75.0 and months > 0:
                delay_risk = max(delay_risk, prob)
                factors.append(f"ML Predictor: High probability of delay ({prob:.1f}%) with expected delay of {months} months.")
        
        # 3. Cost Risk
        cost_risk, cost_factor = calculate_cost_risk(db, w, category_medians)
        if cost_risk > 50.0:
            factors.append(f"WARNING: {cost_factor}")

        # 4. Duplicate Risk
        dup_risk = 0.0
        duplicates = find_duplicate_works(db, w, threshold=0.55, candidate_pool=works)
        if duplicates:
            highest_dup = duplicates[0]
            dup_risk = min(92.5, highest_dup["duplicate_probability"])
            factors.append(f"CRITICAL: High potential duplicate work ({dup_risk:.1f}% similarity) found {highest_dup['distance_km'] or 0:.2f} km away ({highest_dup['work_id']}).")

        # 5. Payment Risk
        payment_risk = 0.0
        if check_payment_burst(w):
            payment_risk = 85.0
            factors.append("WARNING: Multiple rapid disbursements made within a 5-day window.")
        
        # Check payment concentration vs physical progress
        if utilization_ratio > 0.7 and phys_prog == 0.0:
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
            compliance_risk = min(92.5, 30.0 + len(missing) * 20.0)
            factors.append(f"Compliance: Missing critical details: {', '.join(missing)}.")

        # 7. Document Risk
        doc_risk = 0.0
        for doc in w.documents:
            if doc.consistency_score is not None:
                d_risk = 100.0 - doc.consistency_score
                if d_risk > doc_risk:
                    doc_risk = d_risk
        if doc_risk > 25.0:
            doc_risk = min(92.5, doc_risk)
            factors.append(f"WARNING: Document integrity discrepancies detected (Consistency score: {100.0 - doc_risk:.1f}%).")

        # 8. Geographic Risk
        geo_risk = 0.0
        neighbors = []
        for other in works:
            if other.id != w.id and other.district_code == w.district_code and w.latitude and w.longitude and other.latitude and other.longitude:
                dist = haversine_distance(w.latitude, w.longitude, other.latitude, other.longitude)
                if dist <= 5.0:
                    neighbors.append(other)
        if neighbors:
            neighbor_risks = []
            for n in neighbors:
                n_util = n.expenditure / n.sanctioned_amount if n.sanctioned_amount > 0 else 0.0
                n_phys = n.physical_progress if n.physical_progress is not None else 0.0
                n_base = 20.0
                if n_util > 0.8 and n_phys < 50:
                    n_base = 75.0
                neighbor_risks.append(n_base)
            avg_neighbor_risk = float(np.mean(neighbor_risks))
            if avg_neighbor_risk >= 65.0:
                geo_risk = min(92.5, avg_neighbor_risk)
                factors.append("Geospatial cluster analysis flags high-risk neighbor concentration in a 5km radius.")

        # Cap all individual sub-scores at 92.5% max limit
        fin_risk = min(92.5, fin_risk)
        delay_risk = min(92.5, delay_risk)
        cost_risk = min(92.5, cost_risk)
        dup_risk = min(92.5, dup_risk)
        payment_risk = min(92.5, payment_risk)
        compliance_risk = min(92.5, compliance_risk)
        doc_risk = min(92.5, doc_risk)
        geo_risk = min(92.5, geo_risk)

        # Validate factors before saving
        validated_factors = validate_factor_correlations(w, factors)

        # Non-Linear Composite Severity Engine
        all_sub_scores = [fin_risk, delay_risk, cost_risk, dup_risk, payment_risk, compliance_risk, doc_risk, geo_risk]
        max_severity = max(all_sub_scores)
        top_3_sub_scores = sorted(all_sub_scores, reverse=True)[:3]
        top_3_mean = float(np.mean(top_3_sub_scores))
        active_sub_scores = [s for s in all_sub_scores if s > 0]
        active_mean = float(np.mean(active_sub_scores)) if active_sub_scores else 0.0

        if max_severity >= 70.0:
            overall_score = max(max_severity * 0.80, (0.50 * max_severity) + (0.30 * top_3_mean) + (0.20 * active_mean))
        elif max_severity >= 40.0:
            overall_score = max(max_severity * 0.70, (0.40 * max_severity) + (0.35 * top_3_mean) + (0.25 * active_mean))
        else:
            overall_score = (0.30 * max_severity) + (0.40 * top_3_mean) + (0.30 * active_mean)

        overall_score = min(92.5, max(0.0, round(overall_score, 1)))

        risk_record = existing_risks.get(w.id)
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
                factors=validated_factors
            )
            db.add(risk_record)
            existing_risks[w.id] = risk_record
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
            risk_record.factors = validated_factors

        # Synchronize Alerts for dashboard alerts overview
        if dup_risk >= 50.0:
            a_key = (w.id, "DUP_WORK")
            if a_key not in existing_alerts:
                a_obj = Alert(work_id=w.id, alert_type="DUP_WORK", severity="CRITICAL", score=dup_risk, reason=f"Potential duplicate work detected ({dup_risk:.1f}% similarity).", status="ACTIVE")
                db.add(a_obj)
                existing_alerts[a_key] = a_obj

        if cost_risk >= 50.0:
            a_key = (w.id, "RULE_COST_OVERRUN")
            if a_key not in existing_alerts:
                a_obj = Alert(work_id=w.id, alert_type="RULE_COST_OVERRUN", severity="HIGH", score=cost_risk, reason=f"Excess cost outlier detected (Risk score: {cost_risk:.1f}).", status="ACTIVE")
                db.add(a_obj)
                existing_alerts[a_key] = a_obj

        if doc_risk >= 25.0:
            a_key = (w.id, "RULE_DOC_MISMATCH")
            if a_key not in existing_alerts:
                a_obj = Alert(work_id=w.id, alert_type="RULE_DOC_MISMATCH", severity="HIGH", score=doc_risk, reason=f"Document integrity discrepancy detected (Risk score: {doc_risk:.1f}).", status="ACTIVE")
                db.add(a_obj)
                existing_alerts[a_key] = a_obj

        if overall_score >= 75.0:
            a_key = (w.id, "CRITICAL_RISK")
            if a_key not in existing_alerts:
                a_obj = Alert(work_id=w.id, alert_type="CRITICAL_RISK", severity="CRITICAL", score=overall_score, reason=f"Critical overall risk score ({overall_score:.1f}/100).", status="ACTIVE")
                db.add(a_obj)
                existing_alerts[a_key] = a_obj

        if idx % 1000 == 0:
            db.flush()

    db.commit()

    # Synchronize Agency table risk_score with composite risk of assigned projects
    from backend.app.models.models import Agency
    agencies = db.query(Agency).all()
    ag_scores = {}
    for w in works:
        if w.implementing_agency_id and w.risk_scores:
            ag_scores.setdefault(w.implementing_agency_id, []).append(w.risk_scores.overall_score)

    for ag in agencies:
        scores = ag_scores.get(ag.id, [])
        if scores:
            ag.risk_score = min(92.5, max(0.0, round((0.50 * max(scores)) + (0.50 * float(np.mean(scores))), 1)))
            db.add(ag)
    db.commit()
