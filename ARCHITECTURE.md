# System Architecture: MPLADS Sentinel AI

This document describes the high-level software architecture, data flow, and modular design of the **MPLADS Sentinel AI** platform.

---

## 1. Modular Block Diagram

The system follows a decoupled, three-tier architecture:
1. **Presentation Layer (React Frontend)**: A modern analytics interface built with TypeScript, Leaflet maps, and Recharts statistics.
2. **Application Layer (FastAPI Backend)**: REST API controllers, session routers, authentication checks, and database session bindings.
3. **Intelligence Layer (AI/ML & OCR Services)**: Run asynchronously or inside API requests, encapsulating statistical models, rule evaluations, and OCR pipelines.

```text
  [ React + TS Frontend ] <----( REST API over JSON )----> [ FastAPI Backend Server ]
                                                                   |
                                                                   +---> [ Database Session ]
                                                                   |            |
                                                                   |            v
                                                                   |     [ PostgreSQL / SQLite ]
                                                                   |
                                                                   +---> [ Rules Engine ]
                                                                   +---> [ Isolation Forest (ML) ]
                                                                   +---> [ Delay Predictor (ML) ]
                                                                   +---> [ Duplicate Finder (NLP/GIS) ]
                                                                   +---> [ OCR & Document Validator ]
```

---

## 2. Dynamic Processing Pipelines

### Data Ingestion & Quality Profiling
```text
CSV/JSON Ingestion ---> Schema Inspector ---> Normalizer ---> Quality Score Evaluator ---> Seeding / Commit
```

### Risk Aggregator & Scoring Engine
```text
Project Record
     |
     +---> Rule Evaluator ----------> Compliance Alerts & Scores (20%)
     |
     +---> Isolation Forest --------> Numerical Anomaly Index (20%)
     |
     +---> Delay Predictor ---------> Expected Overdue Delay (20%)
     |
     +---> Similar Project Finder --> Duplicate Probabilities (15%)
     |
     +---> Cost Deviation Index ----> Comparables Deviation (15%)
     |
     +---> Document Validator -------> Verification Integrity (5%)
     |
     +---> Geospatial Density -------> Proximity Clustering (5%)
     |
     v
[ Weighted Score Aggregator ] ---> [ Unified Risk Score (0-100) ] ---> [ Explainable AI Reasons ]
```

### Document Verification Center
```text
Sanction PDF Upload ---> Text Parser / OCR ---> Entity Extractor ---> DB Cross-Validator ---> Mismatch Alerts
```

---

## 3. Technology Stack Summary

- **Frontend**: React 18, Vite, TypeScript, Lucide Icons, Leaflet (Map overlays), Recharts (KPI trends & cost percentiles).
- **Backend**: FastAPI (Python 3.12), SQLAlchemy (ORM), Pydantic (data validation), Uvicorn (ASGI web server).
- **Database**: PostgreSQL (PostGIS) or SQLite (file-based fallback for direct out-of-the-box local setup).
- **AI/ML/NLP**: Scikit-Learn (Isolation Forest & Random Forest), Pandas/Numpy (matrices), TfidfVectorizer (description similarities), pdfplumber (digital text extraction), pytesseract (OCR processing).
