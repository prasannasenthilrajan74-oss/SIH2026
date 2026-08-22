# REST API Reference

The backend exposes a clean REST API surface for authentication, dashboard metrics, project listings, rule configuration, case management, and AI chatbot routing.

---

## 1. Authentication Endpoints
- **`POST /api/auth/login`**: Authenticate credentials (JSON body) and retrieve a JWT token.
- **`POST /api/auth/token`**: Authenticate credentials (URL form-encoded) and retrieve a JWT token.
- **`GET /api/auth/me`**: Get currently authenticated user details and active role.
- **`GET /api/auth/users`**: List all district/investigation officers (used for case assignments).

---

## 2. Analytics & Dashboard Endpoints
- **`GET /api/dashboard/overview`**: Retrieve KPI summaries (Total Works, expenditure, active alerts) filtered by user role scope.
- **`GET /api/dashboard/heatmap`**: Get GPS coordinates of all projects alongside their overall risk score.

---

## 3. Projects Endpoints
- **`GET /api/works/`**: List all projects. Supports query parameters for state, district, constituency, category, status, risk_level, search query, limit, and offset.
- **`GET /api/works/{id}`**: Get 360-degree detailed work records (dates, progress, cost estimates).
- **`GET /api/works/{id}/payments`**: Get full disbursement transaction histories for a work.
- **`GET /api/works/{id}/documents`**: Get metadata and OCR consistency logs of all orders uploaded.
- **`GET /api/works/{id}/similar`**: Execute hybrid NLP duplicate search for a target project.

---

## 4. Documents & OCR Endpoints
- **`POST /api/documents/upload`**: Upload a sanction PDF order, perform text extraction, parse entities, cross-validate against database values, and update risk scoring profiles.
- **`POST /api/documents/{id}/process`**: Re-run OCR analysis on an existing document record.
- **`GET /api/documents/{id}/extractions`**: Retrieve side-by-side consistency check results.

---

## 5. Case Management Endpoints
- **`GET /api/investigations/`**: List case investigations. Filterable by status.
- **`POST /api/investigations/`**: Open a new investigation case file for a project.
- **`PUT /api/investigations/{id}`**: Update case status, findings, actions, and log to the audit log.

---

## 6. AI Assistant & Rules Endpoints
- **`POST /api/ai/query`**: Execute natural language queries over the database using the AI Sentinel chatbot.
- **`GET /api/rules/`**: List all stored detection rules.
- **`PUT /api/rules/{id}`**: Edit condition thresholds or toggle a rule (enabled/disabled).
- **`POST /api/rules/evaluate`**: Manually trigger rule re-evaluations and risk recalculations on all projects.
