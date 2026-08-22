# MPLADS Sentinel AI

### *"From Passive Monitoring to Proactive Governance"*

---

## 1. Problem Statement & Solution Overview

### Problem Statement ID: 26102
**Title:** Development of an AI-powered system to detect anomalies, fraud, and inefficiencies in MPLAD Scheme implementation
**Organization:** MoSPI
**Department:** Data Informatics & Innovation Division (DIID)

### The Solution
**MPLADS Sentinel AI** is a government-grade AI-powered early-warning and investigation governance layer. It analyzes project, financial, progress, payment, geographic, and document metadata to flag anomalies, cost deviations, delays, duplicate works, and document discrepancies. 

It implements a **human-in-the-loop** paradigm: AI models detect risk, compile evidence, and explain scores; human investigator officers manage cases and log resolution audits.

---

## 2. Core Architecture

The system follows a modular, three-tier software design:

```text
                    MPLADS DATA
                        |
          +-------------+-------------+
          |             |             |
      Structured      PDF/DOC       Images
         Data         Documents
          |             |             |
          v             v             v
      Data ETL       OCR Engine    Image Processing
          |             |
          +------+------+
                 |
                 v
          DATA QUALITY LAYER
                 |
        +--------+---------+
        |                  |
        v                  v
   RULE ENGINE         AI/ML ENGINE
        |                  |
        |       +----------+-----------+
        |       |          |           |
        |       v          v           v
        |    Anomaly     NLP       Prediction
        |    Detection   Similarity
        |       |          |
        +-------+----------+
                |
                v
          RISK SCORING ENGINE
                |
                v
       EXPLAINABLE AI LAYER
                |
       +--------+---------+
       |        |         |
       v        v         v
   Dashboard  Alerts   Reports
                |
                v
        HUMAN INVESTIGATION
                |
                v
         ACTION / RESOLUTION
```

Detailed architectural designs can be found in [ARCHITECTURE.md](file:///c:/Users/prasa/SIH2026/ARCHITECTURE.md).

---

## 3. Technology Stack

- **Frontend**: React, Vite, TypeScript, Leaflet (GPS Heatmaps), Recharts (KPI stats), Vanilla CSS layout.
- **Backend**: FastAPI (Python 3.12), SQLAlchemy, Pydantic validation.
- **Database**: PostgreSQL (PostGIS) or SQLite file-based fallback for immediate local runs.
- **AI/ML/NLP**: Scikit-Learn (Isolation Forest outlier detection, Random Forest delay forecasting), TfidfVectorizer Cosine Text similarities, Haversine spatial distance calculations.
- **OCR Engine**: pdfplumber (digital PDF extraction) with pytesseract OCR fallbacks.

---

## 4. Setup & Running Locally

### Prerequisites
- Node.js (v18+)
- Python (v3.12+)

### Backend Installation & Setup
1. Open a terminal in the root folder.
2. Initialize virtual environment:
   ```bash
   py -3.12 -m venv .venv
   ```
3. Activate virtual environment:
   - **Windows PowerShell**: `.venv\Scripts\Activate.ps1`
   - **Command Prompt**: `.venv\Scripts\activate.bat`
4. Install pip requirements:
   ```bash
   pip install -r requirements.txt
   ```
5. Run backend:
   ```bash
   python backend/run.py
   ```
   *The server boots at `http://localhost:8000`. On startup, it automatically initializes tables and seeds the database with 1,000+ realistic works and synthetic anomalies.*

### Frontend Installation & Setup
1. Open a new terminal in the `frontend/` folder.
2. Install npm packages:
   ```bash
   npm install
   ```
3. Run React development server:
   ```bash
   npm run dev
   ```
   *The client runs at `http://localhost:3000`.*

---

## 5. Demo Credentials

To test role-specific dashboards, log in with these accounts (password is same as username):
- **Ministry Admin**: `admin` / `admin123`
- **State Nodal (Tamil Nadu)**: `state_nodal` / `state123`
- **District Authority (Chennai)**: `district_auth` / `district123`
- **MP Viewer (Chennai South)**: `mp_viewer` / `mp123`
- **Investigation Officer**: `investigator` / `investigator123`

---

## 6. Project Documentation
- **Architecture Specification**: [ARCHITECTURE.md](file:///c:/Users/prasa/SIH2026/ARCHITECTURE.md)
- **AI/ML Modeling Details**: [AI_METHODOLOGY.md](file:///c:/Users/prasa/SIH2026/AI_METHODOLOGY.md)
- **API Endpoint Reference**: [API.md](file:///c:/Users/prasa/SIH2026/API.md)
- **Database Schema**: [DATABASE.md](file:///c:/Users/prasa/SIH2026/DATABASE.md)
- **OCR Verification Pipeline**: [OCR_PIPELINE.md](file:///c:/Users/prasa/SIH2026/OCR_PIPELINE.md)
- **Rules Engine Specifications**: [RULE_ENGINE.md](file:///c:/Users/prasa/SIH2026/RULE_ENGINE.md)
