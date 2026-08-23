import sys
sys.path.insert(0, '.')

from backend.app.db.session import engine, SessionLocal
from backend.app.models.models import Base, Work, RiskScore, Payment, Document, Alert
from backend.app.db.seed import seed_db
from backend.app.services.risk import update_all_risk_scores

print("=== RE-SEEDING DATABASE WITH CLEAN GROUND TRUTH ANOMALIES ===", flush=True)

# Delete all tables to force completely clean fresh seed
db = SessionLocal()
try:
    db.query(Alert).delete()
    db.query(Document).delete()
    db.query(Payment).delete()
    db.query(RiskScore).delete()
    db.query(Work).delete()
    db.commit()
    print("Cleared existing works, payments, documents, alerts, and risk scores.", flush=True)
finally:
    db.close()

# Re-seed database
db = SessionLocal()
try:
    seed_db(db)
    print("Database seeded with fresh ground-truth synthetic data.", flush=True)
finally:
    db.close()

# Calculate fresh risk scores
db = SessionLocal()
try:
    update_all_risk_scores(db)
    print("All risk scores recalculated with Non-Linear Composite Severity Engine.", flush=True)
finally:
    db.close()

print("Reseed complete.", flush=True)
