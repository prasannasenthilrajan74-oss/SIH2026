import re
import numpy as np
from sqlalchemy.orm import Session
from backend.app.models.models import Work, District, State, Agency, RiskScore, Alert, Document, SystemSetting
from backend.app.nlp.similarity import find_duplicate_works
from backend.app.nlp.ollama import query_ollama, get_ollama_status

def query_assistant(db: Session, query: str) -> dict:
    query_lower = query.lower()
    work_id_match = re.search(r'MPLADS-\d{4}-\d{4,5}', query, re.IGNORECASE)
    
    context_str = ""
    sources = []
    base_answer = ""

    # 1. Why is project X high risk?
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
        
        breakdown_text = f"""
- **Financial Risk:** {risk.financial_risk:.1f}/100
- **Delay Risk:** {risk.delay_risk:.1f}/100
- **Cost Overrun Risk:** {risk.cost_risk:.1f}/100
- **Duplicate Risk:** {risk.duplicate_risk:.1f}/100
- **Payment Burst Risk:** {risk.payment_risk:.1f}/100
- **Compliance Risk:** {risk.compliance_risk:.1f}/100
- **Document Integrity Risk:** {risk.document_risk:.1f}/100
- **Geographic Cluster Risk:** {risk.geographic_risk:.1f}/100
""".strip()

        context_str = f"Project ID: {work.id}\nDescription: {work.description}\nMP: {work.mp_name} ({work.constituency})\nOverall Risk Score: {risk.overall_score:.1f}/100\nSub-Risk Breakdown:\n{breakdown_text}\nFactors:\n{factors_text}\nSanctioned Amount: Rs.{work.sanctioned_amount:.2f}\nExpenditure: Rs.{work.expenditure:.2f}\nPhysical Progress: {work.physical_progress:.1f}%\nFinancial Progress: {work.financial_progress:.1f}%"
        
        base_answer = f"""### Risk Profile Audit Analysis: **{work.id}**

**Overall Composite Risk Score:** **{risk.overall_score:.1f}/100** ({get_risk_level(risk.overall_score)})

#### 📊 Sub-Risk Dimension Breakdown:
{breakdown_text}

#### 🚨 Machine Learning & Rule-Engine Drivers:
{factors_text}

#### 💡 Project Financial Execution Status:
- **Sanctioned Allocation:** ₹{(work.sanctioned_amount/100000):,.2f} Lakh
- **Disbursed Expenditure:** ₹{(work.expenditure/100000):,.2f} Lakh ({work.financial_progress:.1f}%)
- **Physical Completion:** {work.physical_progress:.1f}%
- **Executing Agency:** {work.implementing_agency.name if work.implementing_agency else 'N/A'}
""".strip()
        sources = [{"title": f"{work.id}: {work.description}", "link": f"/projects/{work.id}"}]

    # 2. Show delayed projects in X state
    elif "delay" in query_lower:
        matched_state = None
        states = db.query(State).all()
        for s in states:
            if s.name.lower() in query_lower or f" {s.code.lower()} " in f" {query_lower} ":
                matched_state = s
                break
        
        state_code = matched_state.code if matched_state else "TN"
        state_name = matched_state.name if matched_state else "Tamil Nadu"

        delayed = db.query(Work).filter(
            Work.state_code == state_code,
            Work.status != "Completed"
        ).join(RiskScore).order_by(RiskScore.delay_risk.desc()).limit(5).all()

        if not delayed:
            return {
                "answer": f"Great news! There are no high-risk delayed projects currently flagged in the state of {state_name}.",
                "sources": []
            }

        context_str = f"Delayed projects in {state_name}:\n" + "\n".join([f"- {w.id}: {w.description} (Risk: {w.risk_scores.overall_score if w.risk_scores else 0:.1f}, Physical: {w.physical_progress:.1f}%)" for w in delayed])
        base_answer = f"Here are the top delayed projects in **{state_name}** based on risk rating:\n\n"
        for w in delayed:
            risk_score = w.risk_scores.overall_score if w.risk_scores else 0.0
            overdue_desc = f" (Expected completion: {w.expected_completion_date.strftime('%d-%b-%Y')})" if w.expected_completion_date else ""
            base_answer += f"1. **{w.id}** - {w.description} | Risk: {risk_score:.1f} | Physical Progress: {w.physical_progress:.1f}%{overdue_desc}\n"
            sources.append({"title": f"{w.id}: {w.description}", "link": f"/projects/{w.id}"})

    # 3. Duplicate works
    elif "duplicate" in query_lower and work_id_match:
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

        context_str = f"Duplicates for {work.id} ({work.description}):\n" + "\n".join([f"- {d['work_id']} ({d['description']}): {d['duplicate_probability']}% match, {d['distance_km']}km away" for d in duplicates[:3]])
        base_answer = f"I found **{len(duplicates)}** potential duplicate works for **{work.id}**:\n\n"
        sources = [{"title": f"Target: {work.id}", "link": f"/projects/{work.id}"}]
        for d in duplicates[:3]:
            base_answer += f"- **{d['work_id']}** (*{d['description']}*)\n  * **Duplicate Probability:** {d['duplicate_probability']}%\n  * **Text Similarity:** {d['text_similarity']*100:.0f}%\n  * **Distance:** {d['distance_km']} km away in {d['district']}\n  * **Sanctioned Amount:** ₹{d['sanctioned_amount']/100000:.1f} Lakh\n\n"
            sources.append({"title": f"Duplicate: {d['work_id']}", "link": f"/projects/{d['work_id']}"})

    # 4. District financial risk
    elif "district" in query_lower:
        results = db.query(
            District.name, State.name, RiskScore.financial_risk
        ).select_from(Work).join(RiskScore).join(District, Work.district_code == District.code).join(State, Work.state_code == State.code).all()
        
        district_map = {}
        for d_name, s_name, f_risk in results:
            key = f"{d_name} ({s_name})"
            district_map.setdefault(key, []).append(f_risk)
            
        avg_district_risks = sorted([(k, np.mean(v), len(v)) for k, v in district_map.items()], key=lambda x: x[1], reverse=True)
        
        context_str = "Top Financial Risk Districts:\n" + "\n".join([f"- {dist}: Avg Risk {score:.1f}/100 ({count} works)" for dist, score, count in avg_district_risks[:5]])
        base_answer = "Here are the districts with the **highest financial risk indices** (averaged across projects):\n\n"
        for idx, (dist, score, count) in enumerate(avg_district_risks[:5]):
            base_answer += f"{idx+1}. **{dist}** - Risk Score: **{score:.1f}/100** (calculated across {count} works)\n"
        sources = [{"title": "Risk Monitor", "link": "/risk-monitor"}]

    # 5. Agency cost deviations
    elif "agency" in query_lower or "agencies" in query_lower:
        agencies = db.query(Agency).filter(Agency.average_cost_deviation > 0.05).order_by(Agency.average_cost_deviation.desc()).limit(5).all()
        if not agencies:
            return {
                "answer": "All implementing agencies are performing within normal cost limits (deviation < 5%).",
                "sources": []
            }
        context_str = "Agency Cost Deviations:\n" + "\n".join([f"- {a.name}: +{a.average_cost_deviation*100:.1f}% deviation, Risk Score {a.risk_score:.1f}/100" for a in agencies])
        base_answer = "Here are the implementing agencies with the **highest average cost deviations** compared to sanctioned estimates:\n\n"
        for idx, a in enumerate(agencies):
            base_answer += f"{idx+1}. **{a.name}** | Cost Deviation: **+{a.average_cost_deviation*100:.1f}%** | Historical Projects: {len(a.works)} | Agency Risk Score: {a.risk_score:.1f}/100\n"
            sources.append({"title": f"Agency: {a.name}", "link": f"/agencies/{a.id}"})

    # 6. Document summary
    elif "document" in query_lower or "summarize" in query_lower or "pdf" in query_lower:
        docs = db.query(Document).order_by(Document.id.desc()).limit(3).all()
        if not docs:
            return {
                "answer": "No documents have been uploaded to summarize yet. Go to the Documents center to upload sanction orders.",
                "sources": []
            }
        latest_doc = docs[0]
        context_str = f"Document: {latest_doc.file_name}, Work ID: {latest_doc.work_id}, Amount: {latest_doc.extracted_data.get('sanctioned_amount')}, Consistency: {latest_doc.consistency_score}%\nOCR Text: {latest_doc.ocr_text[:300]}"
        base_answer = f"Here is a summary of the latest uploaded document **{latest_doc.file_name}** associated with project **{latest_doc.work_id or 'N/A'}**:\n\n" \
                      f"- **Document Type:** {latest_doc.document_type}\n" \
                      f"- **Extracted Work ID:** {latest_doc.extracted_data.get('work_id', 'Not found')}\n" \
                      f"- **Extracted Cost:** ₹{latest_doc.extracted_data.get('sanctioned_amount', 0.0)/100000:.1f} Lakh\n" \
                      f"- **Extracted Date:** {latest_doc.extracted_data.get('sanction_date', 'N/A')}\n" \
                      f"- **Extracted Agency:** {latest_doc.extracted_data.get('agency', 'N/A')}\n" \
                      f"- **Document Consistency Rating:** **{latest_doc.consistency_score or 0.0:.1f}%**\n\n" \
                      f"*Summary of contents:* {latest_doc.ocr_text[:200]}..."
        sources = [{"title": latest_doc.file_name, "link": f"/projects/{latest_doc.work_id}"}]

    else:
        context_str = "Platform overview: MPLADS Sentinel AI tracks 1,000+ infrastructure projects, 764 Members of Parliament across 36 States/UTs, anomaly detection scores, risk evaluation rules, and OCR document verification."
        base_answer = "Hello! I am **Sentinel AI**, your virtual assistant powered by local Ollama LLM integration. Try asking:\n" \
                      "- *\"Why is project MPLADS-2026-0007 high risk?\"*\n" \
                      "- *\"Which districts have the highest financial risk?\"*\n" \
                      "- *\"Show delayed projects in Tamil Nadu.\"*\n" \
                      "- *\"Which agencies have unusually high cost deviations?\"*\n" \
                      "- *\"Find possible duplicate works near MPLADS-2026-0025.\"*\n" \
                      "- *\"Summarize the latest document.\"*"

    # 1. Attempt Google Gemini API Generation if key configured
    from backend.app.nlp.gemini import query_gemini_api
    gemini_res = query_gemini_api(
        prompt=f"User Query: {query}\n\nGround-Truth Database Context:\n{context_str}\n\nPlease generate a clear, concise, professional answer for the platform dashboard user.",
        system_prompt="You are Sentinel AI, an expert AI governance assistant for the MPLADS platform. Provide clear, accurate answers grounded strictly in the provided ground-truth context."
    )
    if gemini_res.get("success") and gemini_res.get("response"):
        final_answer = gemini_res["response"] + f"\n\n---\n*⚡ Generated via Google Gemini API (`{gemini_res['model']}`)*"
        return {"answer": final_answer, "sources": sources}

    # 2. Attempt Ollama LLM Generation
    ollama_result = query_ollama(
        prompt=f"User Query: {query}\n\nGround-Truth Database Context:\n{context_str}\n\nPlease generate a clear, professional answer.",
        system_prompt="You are Sentinel AI, an expert AI governance assistant for the MPLADS platform. Provide clear, accurate answers grounded strictly in the provided ground-truth context."
    )

    ollama_status = get_ollama_status()
    ollama_notice = ""
    if ollama_status["running"]:
        if ollama_status["models"]:
            ollama_notice = f"\n\n---\n*🤖 Synthesized via local Ollama LLM model: `{ollama_status['models'][0]}`*"
        else:
            ollama_notice = f"\n\n---\n*💡 Local Ollama service connected (`{ollama_status['url']}`). Add `GEMINI_API_KEY=your_key` in `.env` to enable Gemini AI.*"
    else:
        ollama_notice = "\n\n---\n*ℹ️ Running in deterministic database mode. Add `GEMINI_API_KEY=your_key` in `.env` or start `ollama serve` to connect LLM models.*"

    if ollama_result.get("success") and ollama_result.get("response"):
        final_answer = ollama_result["response"] + f"\n\n---\n*🤖 Generated via local Ollama model `{ollama_result['model']}`*"
        return {"answer": final_answer, "sources": sources}

    # Return structured base answer + connectivity status
    return {"answer": base_answer + ollama_notice, "sources": sources}

def get_risk_level(score: float) -> str:
    if score >= 85:
        return "🔴 CRITICAL"
    elif score >= 70:
        return "🟠 HIGH"
    elif score >= 45:
        return "🟡 MEDIUM"
    else:
        return "🟢 LOW"
