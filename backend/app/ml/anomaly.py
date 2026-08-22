import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sqlalchemy.orm import Session
from backend.app.models.models import Work, RiskScore
import datetime

class AnomalyDetector:
    def __init__(self, n_estimators=100, contamination=0.08, random_state=42):
        self.n_estimators = n_estimators
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            random_state=self.random_state
        )
        self.is_fitted = False

    def _prepare_features(self, works: list[Work]) -> pd.DataFrame:
        data = []
        today = datetime.date.today()
        for w in works:
            # Basic variables
            utilization_ratio = w.expenditure / w.sanctioned_amount if w.sanctioned_amount > 0 else 0.0
            
            # Delay calculation
            delay_days = 0.0
            if w.status != 'Completed' and w.expected_completion_date:
                if today > w.expected_completion_date:
                    delay_days = (today - w.expected_completion_date).days
            elif w.status == 'Completed' and w.actual_completion_date and w.expected_completion_date:
                delay_days = (w.actual_completion_date - w.expected_completion_date).days
                if delay_days < 0:
                    delay_days = 0.0
                    
            cost_deviation = 0.0
            if w.estimated_cost > 0:
                cost_deviation = (w.sanctioned_amount - w.estimated_cost) / w.estimated_cost

            data.append({
                "work_id": w.id,
                "sanctioned_amount": w.sanctioned_amount,
                "expenditure": w.expenditure,
                "utilization_ratio": utilization_ratio,
                "physical_progress": w.physical_progress,
                "financial_progress": w.financial_progress,
                "delay_days": delay_days,
                "cost_deviation": cost_deviation
            })

        df = pd.DataFrame(data)
        return df

    def fit_predict(self, db: Session) -> dict[str, float]:
        works = db.query(Work).all()
        if len(works) < 10:
            # Fallback if too few records to fit Isolation Forest
            print("Too few works to train Isolation Forest. Using simple statistical fallback.")
            scores = {}
            for w in works:
                # Simple heuristic score
                score = 0.0
                if w.financial_progress > 80 and w.physical_progress < 50:
                    score += 50.0
                if w.expenditure > w.sanctioned_amount:
                    score += 30.0
                scores[w.id] = min(99.0, score + random.uniform(5.0, 15.0))
            return scores

        df = self._prepare_features(works)
        feature_cols = [
            "sanctioned_amount", "expenditure", "utilization_ratio", 
            "physical_progress", "financial_progress", "delay_days", "cost_deviation"
        ]
        
        X = df[feature_cols].fillna(0).values
        
        # Fit model
        self.model.fit(X)
        self.is_fitted = True
        
        # Isolation Forest decision_function returns negative values for anomalies (lower is more anomalous)
        raw_scores = self.model.decision_function(X)
        
        # Map raw scores to 0-100 scale: higher means more anomalous
        # decision_function output is roughly in range [-0.5, 0.5]
        min_raw = np.min(raw_scores)
        max_raw = np.max(raw_scores)
        
        # Avoid division by zero
        if max_raw == min_raw:
            scaled_scores = np.ones(len(raw_scores)) * 50.0
        else:
            # Invert so lower decision function (more anomalous) becomes higher score
            scaled_scores = 100.0 * (1.0 - (raw_scores - min_raw) / (max_raw - min_raw))
            # Smooth scores
            scaled_scores = np.clip(scaled_scores, 0, 100)

        # Build map
        results = {}
        for idx, row in df.iterrows():
            results[row["work_id"]] = float(scaled_scores[idx])

        return results
def run_anomaly_detector(db: Session) -> dict[str, float]:
    detector = AnomalyDetector()
    return detector.fit_predict(db)
