import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sqlalchemy.orm import Session
from backend.app.models.models import Work, Agency
import datetime

class DelayPredictor:
    def __init__(self, random_state=42):
        self.random_state = random_state
        self.model = RandomForestRegressor(n_estimators=50, random_state=self.random_state)
        self.is_fitted = False

    def train_and_predict(self, db: Session) -> dict[str, dict]:
        # 1. Fetch completed works for training
        completed_works = db.query(Work).filter(
            Work.status == "Completed",
            Work.sanction_date.isnot(None),
            Work.expected_completion_date.isnot(None),
            Work.actual_completion_date.isnot(None)
        ).all()

        all_works = db.query(Work).all()
        today = datetime.date.today()

        # Fallback if insufficient training data
        if len(completed_works) < 15:
            # Deterministic heuristic fallback
            predictions = {}
            for w in all_works:
                if w.status == "Completed":
                    predictions[w.id] = {"delay_probability": 0.0, "predicted_delay_months": 0.0}
                    continue
                
                # Heuristic estimation
                if not w.sanction_date or not w.expected_completion_date:
                    predictions[w.id] = {"delay_probability": 30.0, "predicted_delay_months": 1.0}
                    continue
                
                expected_days = (w.expected_completion_date - w.sanction_date).days
                if expected_days <= 0:
                    expected_days = 180
                
                elapsed_days = (today - w.sanction_date).days
                if elapsed_days < 0:
                    elapsed_days = 0

                elapsed_ratio = elapsed_days / expected_days if expected_days > 0 else 0.0
                
                # Delay probability logic
                delay_prob = 10.0
                pred_delay = 0.0
                
                if elapsed_ratio > 0.5 and w.physical_progress < 20:
                    delay_prob = 65.0
                    pred_delay = 3.5
                if elapsed_ratio > 0.8 and w.physical_progress < 50:
                    delay_prob = 85.0
                    pred_delay = 5.0
                if elapsed_ratio > 1.0:
                    delay_prob = 95.0
                    pred_delay = (elapsed_days - expected_days) / 30.0 + 2.0
                
                predictions[w.id] = {
                    "delay_probability": float(min(99.0, max(0.0, delay_prob))),
                    "predicted_delay_months": float(round(pred_delay, 1))
                }
            return predictions

        # 2. Build training dataset
        train_data = []
        for w in completed_works:
            expected_days = (w.expected_completion_date - w.sanction_date).days
            actual_days = (w.actual_completion_date - w.sanction_date).days
            delay_days = max(0, actual_days - expected_days)
            delay_months = delay_days / 30.0

            # Features
            train_data.append({
                "sanctioned_amount": w.sanctioned_amount,
                "expected_duration": expected_days,
                "category_hash": hash(w.category) % 100,
                "agency_id": w.implementing_agency_id or 0,
                "delay_months": delay_months
            })

        df_train = pd.DataFrame(train_data)
        X_train = df_train[["sanctioned_amount", "expected_duration", "category_hash", "agency_id"]].fillna(0).values
        y_train = df_train["delay_months"].values

        # Train Random Forest Regressor
        self.model.fit(X_train, y_train)
        self.is_fitted = True

        # 3. Predict for all works
        predictions = {}
        for w in all_works:
            if w.status == "Completed":
                predictions[w.id] = {"delay_probability": 0.0, "predicted_delay_months": 0.0}
                continue

            if not w.sanction_date or not w.expected_completion_date:
                predictions[w.id] = {"delay_probability": 50.0, "predicted_delay_months": 3.0}
                continue

            expected_days = (w.expected_completion_date - w.sanction_date).days
            elapsed_days = (today - w.sanction_date).days
            elapsed_days = max(0, elapsed_days)

            # Predict base potential delay using RF model
            x_pred = np.array([[w.sanctioned_amount, expected_days, hash(w.category) % 100, w.implementing_agency_id or 0]])
            pred_delay_months = float(self.model.predict(x_pred)[0])

            # Adjust prediction based on current progress
            elapsed_ratio = elapsed_days / expected_days if expected_days > 0 else 0.0
            progress_ratio = w.physical_progress / 100.0

            # Calculate delay probability
            delay_probability = 10.0
            if elapsed_ratio > 0:
                # If progress is lagging behind elapsed time
                lag = elapsed_ratio - progress_ratio
                if lag > 0.2:
                    delay_probability = 60.0 + lag * 30.0
                elif lag > 0:
                    delay_probability = 30.0 + lag * 100.0
                else:
                    delay_probability = 15.0

            if elapsed_ratio >= 1.0 and w.physical_progress < 100.0:
                delay_probability = 95.0
                overdue_months = (elapsed_days - expected_days) / 30.0
                pred_delay_months = max(pred_delay_months, overdue_months) + 1.5

            predictions[w.id] = {
                "delay_probability": float(min(99.0, max(5.0, delay_probability))),
                "predicted_delay_months": float(round(max(0.0, pred_delay_months), 1))
            }

        return predictions

def predict_delays(db: Session) -> dict[str, dict]:
    predictor = DelayPredictor()
    return predictor.train_and_predict(db)
