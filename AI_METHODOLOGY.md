# AI & Machine Learning Methodology

This document outlines the specific modeling strategies, feature engineering techniques, and explainability algorithms deployed inside the **MPLADS Sentinel AI** platform.

---

## 1. Multi-Dimensional Anomaly Detection (Isolation Forest)
To flag numerical anomalies and suspicious funding patterns without labeled historical fraud cases, the system utilizes an unsupervised **Isolation Forest** model from `scikit-learn`.

### Feature Engineering
For each work, a feature vector is constructed containing:
- **Sanctioned Amount ($x_1$)**: Scale of the project.
- **Expenditure ($x_2$)**: Capital spent.
- **Utilization Ratio ($x_3$)**: $\frac{Expenditure}{Sanctioned Amount}$.
- **Physical Progress ($x_4$)**: Completeness of the site ($0-100$).
- **Financial Progress ($x_5$)**: Disbursements completeness ($0-100$).
- **Delay Days ($x_6$)**: Number of days overdue beyond expected completion.
- **Cost Deviation ($x_7$)**: Relative deviation from the estimated cost.

### Decision Scoring & Scaling
The Isolation Forest isolates outliers by randomly selecting a feature and split value. Anomalies partition near the root of the trees.
- Raw outlier scores in range $[-0.5, 0.5]$ are min-max inverted and mapped to a $0 - 100$ scale.
- Higher scores represent severe deviations from typical multi-dimensional project progress profiles.

---

## 2. Project Delay Prediction
For ongoing projects, the system runs a **Random Forest Regressor** to forecast expected overdue delays.

### Training Features
- Sanctioned cost amount.
- Expected project duration (days).
- Project Category hash code (drinking water, roads, health, etc.).
- Implementing Agency ID.
- Target value: Overdue months (actual completion date - expected completion date).

### Prediction & Probability Adjustment
- The regressor estimates the expected delay duration in months.
- The delay probability is computed dynamically:
  - If a project is ongoing and overdue, probability locks to $95\%$.
  - Otherwise, it evaluates the ratio of elapsed duration vs current physical progress. Lagging progress increases the probability curve exponentially.

---

## 3. Duplicate Work Detection
Duplicates are flagged using a combined textual, geospatial, and financial similarity matrix:
1. **Description Similarity ($S_{text}$)**: TF-IDF + Cosine Similarity of project strings.
2. **Proximity Similarity ($S_{geo}$)**: Haversine distance ($D$ in km) between project locations, mapped via an exponential decay:
   $$S_{geo} = e^{-0.35 \times D}$$
3. **Cost Similarity ($S_{cost}$)**: $1.0 - \frac{|Amount_A - Amount_B|}{max(Amount_A, Amount_B)}$
4. **Time Overlap ($S_{time}$)**: Evaluates chronological proximity of dates.

The unified duplicate probability is a weighted sum:
$$P_{dup} = 0.45 \cdot S_{text} + 0.25 \cdot S_{geo} + 0.20 \cdot S_{cost} + 0.10 \cdot S_{time}$$

---

## 4. Explainable Risk Scores
Instead of opaque AI scores (e.g. "Fraud Probability = 92%"), every flagged indicator records a clear natural language reasoning point, linking model inputs to outcomes. Contributing factors explain precisely why the score is high (e.g. cost outliers, progress mismatches, or proximity to similar projects).

---

## 5. Root-Cause Backtracking & Explainable Governance Architecture

A core architectural principle of MPLADS Sentinel AI is **hybrid explainability**:

1. **ML Signal Generation (Project Level)**:
   - **Isolation Forest** isolates multi-dimensional numerical outliers.
   - **Random Forest Regressor** predicts future project delay risk.
   - **NLP & Spatial Models** detect semantic and physical duplicates.
   
2. **Statistical Root-Cause Backtracking (Group Level)**:
   - The backtracking engine calculates statistical ratio aggregations (e.g., agency/district anomaly rates vs. regional/national peer averages).
   - **Why Statistical & Ratio-Based?** Root-cause tracing is deliberately statistical rather than a black-box model to preserve 100% auditability, transparency, and legal defensibility when presenting evidence to auditors, investigators, or judicial authorities ("here are the exact two numbers being compared" vs. "the model said so").

### Component Architecture Matrix

| Component | Methodology | Primary Responsibility |
|---|---|---|
| **Project Anomaly Detection** | Isolation Forest (ML) | Flags *what* individual projects exhibit multi-dimensional anomalous patterns |
| **Delay Prediction** | Random Forest Regressor (ML) | Forecasts future overdue risk on ongoing projects |
| **Duplicate Detection** | NLP (TF-IDF) + Haversine (ML/GIS) | Identifies duplicate or overlapping project proposals |
| **Root-Cause Backtracking** | Statistical Group-Average Ratios | Explains *where* flagged anomalies concentrate (agency or district level) |

