from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.db.session import engine, SessionLocal
from backend.app.models.models import Base
from backend.app.db.seed import seed_db
from backend.app.rules.engine import run_rules_on_work
from backend.app.services.risk import update_all_risk_scores

from backend.app.api import auth, dashboard, works, documents, rules, alerts, investigations, agencies, ai, system

# Initialize tables & seed database on start
print("Initializing database tables...")
Base.metadata.create_all(bind=engine)

print("Checking database seed status...")
db = SessionLocal()
try:
    seed_db(db)
    
    # Run initial analysis to populate risk scores
    from backend.app.models.models import RiskScore, Work
    rs_count = db.query(RiskScore).count()
    if rs_count == 0:
        print("No risk scores found. Running initial rules engine and ML anomaly scoring...")
        all_works = db.query(Work).all()
        for w in all_works:
            run_rules_on_work(db, w)
        update_all_risk_scores(db)
        print("Initial risk profiles successfully compiled.")
finally:
    db.close()

app = FastAPI(
    title="MPLADS Sentinel AI API",
    description="Early-warning anomaly & risk detection layer for MPLAD Scheme governance",
    version="1.0.0"
)

# CORS middleware config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In development, allow all. In production, restrict to frontend domain.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(works.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(rules.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(investigations.router, prefix="/api")
app.include_router(agencies.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(system.router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "MPLADS Sentinel AI Governance Platform API",
        "version": "1.0.0"
    }
