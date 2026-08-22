# Rule Engine Specification

The **MPLADS Sentinel AI** platform implements a configurable, database-backed Rules Engine. This allows system administrators to adjust thresholds, enable/disable checks, and add new compliance rules without modifying backend application source code.

---

## 1. Relational Rule Schema
Rules are stored in the `rules` database table:
- `id` (Primary Key, unique code like `RULE_DELAY`)
- `name` (Friendly rule title)
- `description` (Detailed alert explanation)
- `category` (Progress, Financial, Payment, Document, Compliance)
- `severity` (CRITICAL, HIGH, MEDIUM, LOW)
- `condition_expression` (Python-evaluable boolean string)
- `threshold` (Numeric check parameter)
- `enabled` (Boolean toggle)

---

## 2. Condition Expression Syntax
Rule conditions are written in Python syntax and evaluated in a restricted namespace context. The evaluation context exposes:
- `work`: The SQLAlchemy project record model.
- `today`: Current system date object.
- `payment_burst_detected(work)`: A helper function returns true if $\ge 3$ payments occurred in a 5-day span.
- `document_mismatch_detected(work)`: A helper function returns true if any linked PDF order has a consistency score $< 90\%$.

### Pre-packaged Compliance Rules

#### Excessive Project Delay (`RULE_DELAY`)
- **Severity**: HIGH
- **Expression**: `work.status != 'Completed' and today > work.expected_completion_date + 90`
- **Description**: Flags ongoing projects that are overdue by more than 90 days.

#### Progress Mismatch (`RULE_FIN_PHYS_MISMATCH`)
- **Severity**: CRITICAL
- **Expression**: `work.financial_progress > 80.0 and work.physical_progress < 50.0`
- **Description**: Flags cases where funds are heavily drawn ($>80\%$) but physical site completion is lagging ($<50\%$).

#### Cost Overrun (`RULE_COST_OVERRUN`)
- **Severity**: CRITICAL
- **Expression**: `work.expenditure > work.sanctioned_amount`
- **Description**: Flags cases where actual expenditures exceed sanctioned estimates.

#### Suspicious Payment Timing (`RULE_PAYMENT_BURST`)
- **Severity**: HIGH
- **Expression**: `payment_burst_detected(work)`
- **Description**: Flags works with rapid payment clusters (milestones disbursed within 5 days).

#### Document Discrepancies (`RULE_DOC_MISMATCH`)
- **Severity**: HIGH
- **Expression**: `document_mismatch_detected(work)`
- **Description**: Flags projects where uploaded sanction letters have cost or date mismatches.
