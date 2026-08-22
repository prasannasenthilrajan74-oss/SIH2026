# Database Schema Reference

The platform is designed around a relational database architecture. In production, it utilizes **PostgreSQL** with **PostGIS** spatial extensions. Locally, it can run on **SQLite** with custom Haversine mathematical distance checks.

---

## 1. Key Table Definitions

### `users`
Stores user records and credentials for authentication.
- `id` (INT, Primary Key)
- `username` (VARCHAR)
- `hashed_password` (VARCHAR)
- `role_id` (INT, FK to `roles`)
- `state` (VARCHAR, Nullable State scope restriction)
- `district` (VARCHAR, Nullable District scope restriction)
- `constituency` (VARCHAR, Nullable constituency scope restriction)

### `works` (Projects)
Stores critical project details, targets, coordinates, and progress.
- `id` (VARCHAR, Primary Key)
- `description` (TEXT)
- `category` (VARCHAR)
- `mp_name` (VARCHAR)
- `constituency` (VARCHAR)
- `state_code` (VARCHAR, FK to `states`)
- `district_code` (VARCHAR, FK to `districts`)
- `latitude` (FLOAT)
- `longitude` (FLOAT)
- `recommendation_date` (DATE)
- `sanction_date` (DATE)
- `expected_completion_date` (DATE)
- `actual_completion_date` (DATE)
- `status` (VARCHAR - Sanctioned, Ongoing, Completed, Suspended)
- `implementing_agency_id` (INT, FK to `agencies`)
- `estimated_cost` (FLOAT)
- `sanctioned_amount` (FLOAT)
- `expenditure` (FLOAT)
- `physical_progress` (FLOAT - percentage completion)
- `financial_progress` (FLOAT - percentage utilization)

### `payments`
Tracks disbursements made to projects.
- `id` (INT, Primary Key)
- `work_id` (VARCHAR, FK to `works`)
- `payment_date` (DATE)
- `amount` (FLOAT)
- `payment_type` (VARCHAR - Milestone, Advance, Final)
- `transaction_ref` (VARCHAR, Unique)

### `risk_scores`
Stores aggregated risk score metrics and explanation details for front-end drill down.
- `work_id` (VARCHAR, Primary Key, FK to `works`)
- `overall_score` (FLOAT)
- `financial_risk` (FLOAT)
- `delay_risk` (FLOAT)
- `cost_risk` (FLOAT)
- `duplicate_risk` (FLOAT)
- `payment_risk` (FLOAT)
- `compliance_risk` (FLOAT)
- `document_risk` (FLOAT)
- `geographic_risk` (FLOAT)
- `factors` (JSON - list of explanation strings)

### `documents`
Stores metadata and parsed outputs of uploaded order PDFs.
- `id` (INT, Primary Key)
- `work_id` (VARCHAR, FK to `works`)
- `document_type` (VARCHAR)
- `file_name` (VARCHAR)
- `file_path` (VARCHAR)
- `ocr_text` (TEXT)
- `extracted_data` (JSON - parsed entities)
- `consistency_score` (FLOAT)

### `investigations`
Case files created by auditors for manual verification actions.
- `id` (INT, Primary Key)
- `work_id` (VARCHAR, FK to `works`)
- `assigned_to` (INT, FK to `users`)
- `priority` (VARCHAR - CRITICAL, HIGH, MEDIUM, LOW)
- `status` (VARCHAR - Detected, Under Review, Assigned, Evidence Requested, Resolved)
- `findings` (TEXT)
- `action_taken` (TEXT)
- `resolution_state` (VARCHAR - False Positive, Escalated, Corrective Action)
- `resolved_at` (TIMESTAMP)
- `created_at` (TIMESTAMP)

### `investigation_actions` (Audit Trail)
Tracks timeline history logs of modifications made to case files.
- `id` (INT, Primary Key)
- `investigation_id` (INT, FK to `investigations`)
- `performed_by` (INT, FK to `users`)
- `action` (VARCHAR)
- `notes` (TEXT)
- `timestamp` (TIMESTAMP)
