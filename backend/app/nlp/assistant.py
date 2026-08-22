import re
from sqlalchemy.orm import Session
from backend.app.models.models import Work, District, State, Agency, RiskScore, Alert, Document
from backend.app.nlp.similarity import find_duplicate_works

def query_assistant(db: Session, query: str) -> dict:
    query_lower = query.lower()
    
    # 1. Why is project X high risk?
    work_id_match = re.search(r'MPLADS-\d{4}-\d{4,5}', query, re.IGNORECASE)
    if work_id_match and ("why" in query_lower or "risk" in query_lower or "explain" in query_lower):
        work_id = work_id_match.group(0).upper()
        work = db.query(Work).filter(Work.id == work_id).first()
        if not work:
            return {
                "answer": f"I couldn't find any project with ID {work_id} in the system database.",
                "sources": []
            }
        
        risk = work.risk_scores
        if not risk:
            return {
                "answer": f"Project {work_id} ({work.description}) does not have a risk profile calculated yet. Please run the analytics engine.",
                "sources": [{"title": work.description, "link": f"/projects/{work.id}"}]
            }
            
        factors_text = "\n".join([f"- {f}" for f in risk.factors]) if risk.factors else "- No anomalies detected. Project is performing within expected parameters."
        answer = f"Project **{work.id}** (*{work.description}*) has an overall risk score of **{risk.overall_score:.1f}/100** ({get_risk_level(risk.overall_score)}).\n\n**Key reasons for this risk score:**\n{factors_text}\n\n**Financial Status:** Utilized ₹{work.expenditure/100000:.1f}L out of sanctioned ₹{work.sanctioned_amount/100000:.1f}L ({work.financial_progress:.1f}% progress vs {work.physical_progress:.1f}% physical progress)."
        return {
            "answer": answer,
            "sources": [{"title": f"{work.id}: {work.description}", "link": f"/projects/{work.id}"}]
        }

    # 2. Show delayed projects in X state
    state_match = None
    if "tamil nadu" in query_lower or " tn " in query_lower:
        state_match = ("TN", "Tamil Nadu")
    elif "delhi" in query_lower or " dl " in query_lower:
        state_match = ("DL", "Delhi")
    elif "maharashtra" in query_lower or " mh " in query_lower:
        state_match = ("MH", "Maharashtra")
    elif "karnataka" in query_lower or " ka " in query_lower:
        state_match = ("KA", "Karnataka")

    if "delay" in query_lower and state_match:
        code, name = state_match
        delayed = db.query(Work).filter(
            Work.state_code == code,
            Work.status != "Completed"
        ).join(RiskScore).order_back(RiskScore.delay_risk.desc()).limit(5).all()
        
        if not delayed:
            return {
                "answer": f"Great news! There are no high-risk delayed projects currently flagged in the state of {name}.",
                "sources": []
            }
            
        ans = f"Here are the top delayed projects in **{name}** based on risk rating:\n\n"
        sources = []
        for w in delayed:
            risk = w.risk_scores
            overdue_desc = ""
            if w.expected_completion_date:
                overdue_desc = f" (Expected completion: {w.expected_completion_date.strftime('%d-%b-%Y')})"
            ans += f"1. **{w.id}** - {w.description} | Risk: {risk.overall_score:.1f} | Physical Progress: {w.physical_progress:.1f}%{overdue_desc}\n"
            sources.append({"title": f"{w.id}: {w.description}", "link": f"/projects/{w.id}"})
        return {"answer": ans, "sources": sources}

    # 3. Find duplicate works near project X
    if "duplicate" in query_lower and work_id_match:
        work_id = work_id_match.group(0).upper()
        work = db.query(Work).filter(Work.id == work_id).first()
        if not work:
            return {"answer": f"Project {work_id} was not found.", "sources": []}
            
        duplicates = find_duplicate_works(db, work, threshold=0.65)
        if not duplicates:
            return {
                "answer": f"I analyzed project **{work.id}** (*{work.description}*) and did not find any potential duplicates with high confidence in the same district.",
                "sources": [{"title": work.description, "link": f"/projects/{work.id}"}]
            }
            
        ans = f"I found **{len(duplicates)}** potential duplicate works for **{work.id}**:\n\n"
        sources = [{"title": f"Target: {work.id}", "link": f"/projects/{work.id}"}]
        for d in duplicates[:3]:
            ans += f"- **{d['work_id']}** (*{d['description']}*)\n  * **Duplicate Probability:** {d['duplicate_probability']}%\n  * **Text Similarity:** {d['text_similarity']*100:.0f}%\n  * **Distance:** {d['distance_km']} km away in {d['district']}\n  * **Sanctioned Amount:** ₹{d['sanctioned_amount']/100000:.1f} Lakh\n\n"
            sources.append({"title": f"Duplicate: {d['work_id']}", "link": f"/projects/{d['work_id']}"})
        return {"answer": ans, "sources": sources}

    # 4. Which districts have the highest financial risk?
    if "district" in query_lower and ("financial risk" in query_lower or "high risk" in query_lower or "fraud" in query_lower):
        # Aggregate risk by district
        results = db.query(
            District.name, State.name, RiskScore.financial_risk
        ).select_from(Work).join(RiskScore).join(District, Work.district_code == District.code).join(State, Work.state_code == State.code).all()
        
        district_map = {}
        for d_name, s_name, f_risk in results:
            key = f"{d_name} ({s_name})"
            if key not in district_map:
                district_map[key] = []
            district_map[key].append(f_risk)
            
        avg_district_risks = []
        for key, risks in district_map.items():
            avg_district_risks.append((key, np.mean(risks), len(risks)))
            
        avg_district_risks.sort(key=lambda x: x[1], reverse=True)
        
        ans = "Here are the districts with the **highest financial risk indices** (averaged across projects):\n\n"
        for idx, (dist, score, count) in enumerate(avg_district_risks[:5]):
            ans += f"{idx+1}. **{dist}** - Risk Score: **{score:.1f}/100** (calculated across {count} works)\n"
            
        return {
            "answer": ans,
            "sources": [{"title": "Risk Monitor", "link": "/risk-monitor"}]
        }

    # 5. Which agencies have unusually high cost deviations?
    if "agencies" in query_lower or "agency" in query_lower or "cost deviation" in query_lower:
        agencies = db.query(Agency).filter(Agency.average_cost_deviation > 0.05).order_by(Agency.average_cost_deviation.desc()).limit(5).all()
        if not agencies:
            return {
                "answer": "All implementing agencies are performing within normal cost limits (deviation < 5%).",
                "sources": []
            }
        ans = "Here are the implementing agencies with the **highest average cost deviations** compared to sanctioned estimates:\n\n"
        sources = []
        for idx, a in enumerate(agencies):
            ans += f"{idx+1}. **{a.name}** | Cost Deviation: **+{a.average_cost_deviation*100:.1f}%** | Historical Projects: {len(a.works)} | Agency Risk Score: {a.risk_score:.1f}/100\n"
            sources.append({"title": f"Agency: {a.name}", "link": f"/agencies/{a.id}"})
        return {"answer": ans, "sources": sources}

    # 6. Summarize document summary
    if "summarize" in query_lower or "document" in query_lower:
        docs = db.query(Document).order_by(Document.id.desc()).limit(3).all()
        if not docs:
            return {
                "answer": "No documents have been uploaded to summarize yet. Go to the Documents center to upload sanction orders.",
                "sources": []
            }
        latest_doc = docs[0]
        ans = f"Here is a summary of the latest uploaded document **{latest_doc.file_name}** associated with project **{latest_doc.work_id or 'N/A'}**:\n\n" \
              f"- **Document Type:** {latest_doc.document_type}\n" \
              f"- **Extracted Work ID:** {latest_doc.extracted_data.get('work_id', 'Not found')}\n" \
              f"- **Extracted Cost:** ₹{latest_doc.extracted_data.get('sanctioned_amount', 0.0)/100000:.1f} Lakh\n" \
              f"- **Extracted Date:** {latest_doc.extracted_data.get('sanction_date', 'N/A')}\n" \
              f"- **Extracted Agency:** {latest_doc.extracted_data.get('agency', 'N/A')}\n" \
              f"- **Document Consistency Rating:** **{latest_doc.consistency_score or 0.0:.1f}%**\n\n" \
              f"*Summary of contents:* {latest_doc.ocr_text[:200]}..."
        return {
            "answer": ans,
            "sources": [{"title": latest_doc.file_name, "link": f"/projects/{latest_doc.work_id}"}]
        }

    # Fallback response
    return {
        "answer": "Hello! I am **Sentinel AI**, your virtual assistant. I can assist you with government-scale analytics. Try asking:\n"
                  "- *\"Why is project MPLADS-2026-0007 high risk?\"*\n" \
                  "- *\"Which districts have the highest financial risk?\"*\n" \
                  "- *\"Show delayed projects in Tamil Nadu.\"*\n" \
                  "- *\"Which agencies have unusually high cost deviations?\"*\n" \
                  "- *\"Find possible duplicate works near MPLADS-2026-0025.\"*\n" \
                  "- *\"Summarize the latest document.\"*",
        "sources": []
    }

def get_risk_level(score: float) -> str:
    if score >= 85:
        return "🔴 CRITICAL"
    elif score >= 70:
        return "🟠 HIGH"
    elif score >= 45:
        return "🟡 MEDIUM"
    else:
        return "🟢 LOW"

import numpy as np
