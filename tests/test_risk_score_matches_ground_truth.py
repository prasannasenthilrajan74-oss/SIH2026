import sys
sys.path.insert(0, '.')
from sqlalchemy.orm import Session
from backend.app.db.session import SessionLocal
from backend.app.models.models import Work, RiskScore
from backend.app.services.risk import update_all_risk_scores

def test_risk_score_matches_ground_truth():
    """
    Automated regression test verifying that risk scores and why-flagged factors correlate 100%
    with project database fields and synthetic ground-truth labels.
    """
    db: Session = SessionLocal()
    try:
        # Recalculate all risk scores in test database
        update_all_risk_scores(db)

        works = db.query(Work).all()
        assert len(works) > 0, "Database contains no works to test."

        mismatches = []
        normal_high_risk_count = 0
        anomalous_low_risk_count = 0

        for work in works:
            rs = work.risk_scores
            assert rs is not None, f"Work {work.id} is missing a RiskScore record."

        import os, pandas as pd
        dataset_path = os.path.join("Dataset", "projects_corrected.csv")
        ground_truth_map = {}
        if os.path.exists(dataset_path):
            df_gt = pd.read_csv(dataset_path)
            ground_truth_map = dict(zip(df_gt['project_id'].astype(str), df_gt['ground_truth_label'].astype(str)))

        for work in works:
            rs = work.risk_scores
            assert rs is not None, f"Work {work.id} is missing a RiskScore record."

            if work.id in ground_truth_map:
                is_synthetic_anomaly = (ground_truth_map[work.id] == "ANOMALOUS")
            else:
                try:
                    i = int(work.id.split('-')[-1])
                except ValueError:
                    i = 1
                is_synthetic_anomaly = (i % 7 == 0) or ("DUP" in work.id) or (i == 26)

            # Ground Truth Check 1: Normal projects must not be scored as High/Critical Risk (>= 70.0)
            if not is_synthetic_anomaly:
                if rs.overall_score >= 70.0:
                    normal_high_risk_count += 1
                    mismatches.append(f"[FALSE POSITIVE] Work {work.id} is normal but scored High Risk: {rs.overall_score:.1f}/100. Factors: {rs.factors}")

            # Ground Truth Check 2: Synthetic anomalous projects must be flagged (>= 35.0 Medium/High/Critical)
            else:
                if rs.overall_score < 35.0:
                    anomalous_low_risk_count += 1
                    mismatches.append(f"[FALSE NEGATIVE] Work {work.id} is synthetic anomaly but scored Low Risk: {rs.overall_score:.1f}/100.")

            # Ground Truth Check 3: Factor Correlation Check (cited values match database fields)
            utilization_pct = (work.expenditure / work.sanctioned_amount * 100.0) if work.sanctioned_amount > 0 else 0.0
            phys_prog = work.physical_progress if work.physical_progress is not None else 0.0

            for factor in rs.factors:
                if "utiliz" in factor.lower() and "physical progress" in factor.lower():
                    # Assert work is actually ongoing and expenditure > physical progress
                    assert work.status == "Ongoing", f"Work {work.id} factor cites utilization but status is {work.status}"
                    assert utilization_pct >= 60.0, f"Work {work.id} factor cites high utilization but actual utilization is {utilization_pct:.1f}%"
                    assert phys_prog < 50.0, f"Work {work.id} factor cites low physical progress but actual is {phys_prog:.1f}%"

                if "exceeds sanctioned allocation" in factor.lower() or "exceeds sanctioned amount" in factor.lower():
                    assert work.expenditure > work.sanctioned_amount, f"Work {work.id} factor cites cost overrun but expenditure (₹{work.expenditure}) <= sanctioned (₹{work.sanctioned_amount})"

        print(f"\n=== GROUND TRUTH VERIFICATION REPORT ===")
        print(f"Total Works Tested: {len(works)}")
        print(f"Normal Projects Flagged High Risk (False Positives): {normal_high_risk_count}")
        print(f"Anomalous Projects Unflagged (False Negatives): {anomalous_low_risk_count}")
        print(f"Total Mismatches Found: {len(mismatches)}")

        assert normal_high_risk_count == 0, f"Found {normal_high_risk_count} normal projects wrongly scored high risk."
        assert len(mismatches) == 0, f"Found {len(mismatches)} risk-reason correlation mismatches:\n" + "\n".join(mismatches[:5])

    finally:
        db.close()

if __name__ == "__main__":
    test_risk_score_matches_ground_truth()
