import datetime
from sqlalchemy.orm import Session
from backend.app.models.models import Work, Payment, Document, Rule, Alert

def check_payment_burst(work: Work) -> bool:
    payments = work.payments
    if len(payments) < 3:
        return False
    # Sort payments by date
    sorted_payments = sorted(payments, key=lambda x: x.payment_date)
    # Check if there is any window of 5 days containing 3 or more payments
    for i in range(len(sorted_payments) - 2):
        delta = sorted_payments[i+2].payment_date - sorted_payments[i].payment_date
        if delta.days <= 5:
            return True
    return False

def check_document_mismatch(work: Work) -> bool:
    documents = work.documents
    for doc in documents:
        if doc.consistency_score is not None and doc.consistency_score < 90.0:
            return True
    return False

def evaluate_rule(rule: Rule, work: Work) -> bool:
    if not rule.enabled:
        return False

    # Build local evaluation context
    today = datetime.date.today()
    
    # Helper functions in eval
    def payment_burst_detected(w):
        return check_payment_burst(w)
        
    def document_mismatch_detected(w):
        return check_document_mismatch(w)

    context = {
        "work": work,
        "today": today,
        "payment_burst_detected": payment_burst_detected,
        "document_mismatch_detected": document_mismatch_detected
    }

    try:
        # Evaluate condition expression safely
        # E.g. "work.financial_progress > 80.0 and work.physical_progress < 50.0"
        result = eval(rule.condition_expression, {"__builtins__": {}}, context)
        return bool(result)
    except Exception as e:
        # In case of evaluation error (e.g. NoneType operations)
        print(f"Error evaluating rule {rule.id} on work {work.id}: {e}")
        return False

def run_rules_on_work(db: Session, work: Work) -> list[Alert]:
    active_rules = db.query(Rule).filter(Rule.enabled == True).all()
    triggered_alerts = []

    for rule in active_rules:
        is_triggered = evaluate_rule(rule, work)
        if is_triggered:
            # Check if alert already exists
            existing_alert = db.query(Alert).filter(
                Alert.work_id == work.id,
                Alert.alert_type == rule.id,
                Alert.status == "ACTIVE"
            ).first()

            if not existing_alert:
                alert = Alert(
                    work_id=work.id,
                    alert_type=rule.id,
                    severity=rule.severity,
                    score=100.0 if rule.severity == "CRITICAL" else (75.0 if rule.severity == "HIGH" else 50.0),
                    reason=rule.description,
                    evidence={"rule_id": rule.id, "threshold": rule.threshold}
                )
                db.add(alert)
                triggered_alerts.append(alert)
    db.commit()
    return triggered_alerts
