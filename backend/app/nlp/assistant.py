import re
import numpy as np
from sqlalchemy.orm import Session
from backend.app.models.models import Work, District, State, Agency, RiskScore, Alert, Document, SystemSetting
from backend.app.nlp.similarity import find_duplicate_works
from backend.app.nlp.ollama import query_ollama, get_ollama_status

def query_assistant(db: Session, query: str) -> dict:
    query_lower = query.lower()
    # Match both old MPLADS-YYYY-NNNNN and new PRJ###### project IDs
    work_id_match = re.search(r'PRJ\d{6}|MPLADS-\d{4}-\d{4,5}', query, re.IGNORECASE)

    def has(*keywords):
        return any(k in query_lower for k in keywords)

    def top_risky_works(limit=5, risk_col=None):
        q = db.query(Work).join(RiskScore)
        if risk_col == 'cost':   q = q.order_by(RiskScore.cost_risk.desc())
        elif risk_col == 'fin':  q = q.order_by(RiskScore.financial_risk.desc())
        elif risk_col == 'delay':q = q.order_by(RiskScore.delay_risk.desc())
        elif risk_col == 'dup':  q = q.order_by(RiskScore.duplicate_risk.desc())
        elif risk_col == 'doc':  q = q.order_by(RiskScore.document_risk.desc())
        else:                    q = q.order_by(RiskScore.overall_score.desc())
        return q.limit(limit).all()
    
    context_str = ""
    sources = []
    base_answer = ""

    # 1. Specific project deep-dive
    if work_id_match and has('why', 'risk', 'explain', 'fraud', 'anomaly', 'issue', 'details'):
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
            
    # 6. Most fraud / highest risk
    elif has("most fraud", "highest fraud", "most risk", "highest risk", "top fraud", "more fraud",
             "which project", "riskiest", "most suspicious", "fraud"):
        works = top_risky_works(limit=7)
        if not works:
            return {"answer": "No risk scores found in database.", "sources": []}
        rows = []
        for w in works:
            rs = w.risk_scores
            d = (w.description or "")[:65]
            rows.append(f"- **{w.id}** | {d} | State: {w.state_code} | Risk: {rs.overall_score:.1f}/100 | {w.status}")
            sources.append({"title": f"{w.id} ({rs.overall_score:.1f})", "link": f"/projects/{w.id}"})
        context_str = "Top high-risk projects:\n" + "\n".join(rows)
        base_answer = "### Top Projects by Risk Score (Potential Fraud Indicators)\n\n" + "\n".join(rows)

    # 7. Cost overrun
    elif has("cost overrun", "over budget", "overspent", "overrun"):
        works = top_risky_works(limit=7, risk_col="cost")
        rows = []
        for w in works:
            rs = w.risk_scores
            sa = w.sanctioned_amount or 1
            ov = (w.expenditure - sa) / sa * 100
            d = (w.description or "")[:55]
            rows.append(f"- **{w.id}** | {d} | Overrun: +{ov:.1f}% | Cost Risk: {rs.cost_risk:.1f}/100")
            sources.append({"title": w.id, "link": f"/projects/{w.id}"})
        context_str = "Cost overrun projects:\n" + "\n".join(rows)
        base_answer = "### Projects with Highest Cost Overrun Risk\n\n" + "\n".join(rows)

    # 8. Fin-phys mismatch
    elif has("mismatch", "financial physical", "money spent", "no progress", "funds but no work"):
        works = (db.query(Work).join(RiskScore)
                 .filter(Work.financial_progress > 50, Work.physical_progress < 25)
                 .order_by(RiskScore.financial_risk.desc()).limit(7).all())
        if not works:
            works = top_risky_works(limit=7, risk_col="fin")
        rows = []
        for w in works:
            d = (w.description or "")[:55]
            rows.append(f"- **{w.id}** | {d} | Financial: {w.financial_progress:.1f}% | Physical: {w.physical_progress:.1f}%")
            sources.append({"title": w.id, "link": f"/projects/{w.id}"})
        context_str = "Fin-phys mismatch:\n" + "\n".join(rows)
        base_answer = "### Financial-Physical Mismatch Projects\n\n*(High funds spent, low physical progress)*\n\n" + "\n".join(rows)

    # 9. Duplicate payment
    elif has("duplicate", "double payment", "paid twice"):
        works = top_risky_works(limit=7, risk_col="dup")
        rows = []
        for w in works:
            rs = w.risk_scores
            d = (w.description or "")[:55]
            rows.append(f"- **{w.id}** | {d} | Dup Risk: {rs.duplicate_risk:.1f}/100")
            sources.append({"title": w.id, "link": f"/projects/{w.id}"})
        context_str = "Dup payment risk:\n" + "\n".join(rows)
        base_answer = "### Projects with Highest Duplicate Payment Risk\n\n" + "\n".join(rows)

    # 10. Vendor collusion
    elif has("vendor", "collusion", "contractor", "same vendor"):
        from backend.app.models.models import Payment
        vendor_map = {}
        for p in db.query(Payment).all():
            if p.transaction_ref:
                vendor_map.setdefault(p.transaction_ref, set()).add(p.work_id)
        top_v = sorted(vendor_map.items(), key=lambda x: len(x[1]), reverse=True)[:7]
        rows = [f"- **{v}** | Appears in **{len(w)} projects**" for v, w in top_v]
        context_str = "Vendors spanning most projects:\n" + "\n".join(rows)
        base_answer = "### Vendor Network Analysis - Collusion Risk\n\n*(Vendors appearing in most projects across agencies/districts)*\n\n" + "\n".join(rows)
        sources = [{"title": "Agency Intelligence", "link": "/agency-intelligence"}]

    # 11. Document mismatches
    elif has("document mismatch", "ocr mismatch", "doc fraud", "invoice fraud", "wrong amount", "document risk"):
        mds = db.query(Document).filter(Document.consistency_score < 75).order_by(Document.consistency_score.asc()).limit(7).all()
        rows = []
        for doc in mds:
            ed = doc.extracted_data or {}
            sanc = float(ed.get("sanctioned_amount") or 0)
            ext  = float(ed.get("extracted_amount")  or 0)
            diff = (ext - sanc) / sanc * 100 if sanc else 0
            rows.append(f"- **{doc.work_id}** | {doc.document_type} | Score: {doc.consistency_score:.1f}% | Diff: +{diff:.1f}%")
            sources.append({"title": f"Doc {doc.work_id}", "link": f"/projects/{doc.work_id}"})
        context_str = "Document mismatches:\n" + "\n".join(rows)
        base_answer = "### Document-DB Mismatches (OCR Integrity Failures)\n\n" + "\n".join(rows)

    # 12. Low utilization
    elif has("low utilization", "unutilized", "unspent", "not spent", "no expenditure"):
        works = (db.query(Work).filter(Work.physical_progress < 5, Work.status != "Completed")
                 .order_by(Work.physical_progress.asc()).limit(7).all())
        rows = []
        for w in works:
            d = (w.description or "")[:55]
            rows.append(f"- **{w.id}** | {d} | Spent: {w.financial_progress:.1f}% | Physical: {w.physical_progress:.1f}%")
            sources.append({"title": w.id, "link": f"/projects/{w.id}"})
        context_str = "Low utilization:\n" + "\n".join(rows)
        base_answer = "### Projects with Very Low Utilization\n\n*(Sanctioned but barely started)*\n\n" + "\n".join(rows)

    # 13. Overview / summary stats
    elif has("overview", "summary", "dashboard", "how many", "statistics", "stats", "total"):
        total = db.query(Work).count()
        completed = db.query(Work).filter(Work.status == "Completed").count()
        ongoing   = db.query(Work).filter(Work.status == "Ongoing").count()
        scores    = [r.overall_score for r in db.query(RiskScore).all()]
        crit = len([s for s in scores if s >= 80])
        high = len([s for s in scores if 60 <= s < 80])
        med  = len([s for s in scores if 40 <= s < 60])
        low  = len([s for s in scores if s < 40])
        aw   = db.query(Work).all()
        ts   = sum(w.sanctioned_amount or 0 for w in aw)
        te   = sum(w.expenditure or 0 for w in aw)
        mm   = db.query(Document).filter(Document.consistency_score < 75).count()
        context_str = (f"Stats: {total} projects Done:{completed} Ongoing:{ongoing} "
                       f"Critical:{crit} High:{high} Med:{med} Low:{low} "
                       f"Sanctioned Rs{ts/10000000:.2f}Cr Spent Rs{te/10000000:.2f}Cr DocMismatch:{mm}")
        base_answer = (f"### MPLADS Sentinel Summary\n\n"
                       f"| Metric | Value |\n|---|---|\n"
                       f"| Total Projects | **{total}** |\n| Completed | {completed} |\n| Ongoing | {ongoing} |\n"
                       f"| Critical Risk | **{crit}** |\n| High Risk | **{high}** |\n| Medium | {med} |\n| Low | {low} |\n"
                       f"| Sanctioned | Rs {ts/10000000:.2f} Cr |\n| Expenditure | Rs {te/10000000:.2f} Cr |\n"
                       f"| Doc Mismatches | {mm} |")
        sources = [{"title": "Overview", "link": "/overview"}]

    # 14. State-wise comparison
    elif has("which state", "state wise", "state-wise", "compare state", "state"):
        results = db.query(Work.state_code, RiskScore.overall_score).join(RiskScore).all()
        sm = {}
        for sc, s in results:
            sm.setdefault(sc, []).append(s)
        top = sorted([(sc, sum(v)/len(v), len(v)) for sc, v in sm.items()], key=lambda x: x[1], reverse=True)[:10]
        rows = [f"- **{sc}** | Avg Risk: {s:.1f}/100 | {c} projects" for sc, s, c in top]
        context_str = "State-wise risk:\n" + "\n".join(rows)
        base_answer = "### State-wise Risk Comparison\n\n" + "\n".join(rows)
        sources = [{"title": "Overview Dashboard", "link": "/overview"}]

    # 15. Investigations
    elif has("investigation", "case", "inquiry", "probe"):
        from backend.app.models.models import Investigation
        invs = db.query(Investigation).order_by(Investigation.created_at.desc()).limit(7).all()
        if not invs:
            base_answer = "No case investigations filed yet."
            context_str = "No investigations."
        else:
            rows = [f"- **{i.title}** | {i.status} | Project: {i.work_id} | Priority: {i.priority}" for i in invs]
            context_str = "Investigations:\n" + "\n".join(rows)
            base_answer = "### Case Investigations\n\n" + "\n".join(rows)
            sources = [{"title": i.title, "link": "/investigations"} for i in invs]

    # 6. Document summary (original - kept for backwards compat)
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
        # Default overview or general queries
        total = db.query(Work).count()
        completed = db.query(Work).filter(Work.status == "Completed").count()
        ongoing = db.query(Work).filter(Work.status == "Ongoing").count()
        scores = [r.overall_score for r in db.query(RiskScore).all()]
        crit = len([s for s in scores if s >= 80])
        high = len([s for s in scores if 60 <= s < 80])
        
        # Pull top 3 riskiest projects for immediate reference
        top_works = db.query(Work).join(RiskScore).order_by(RiskScore.overall_score.desc()).limit(3).all()
        top_works_str = "\n".join([f"- **{w.id}**: {w.description[:50]} (Risk: {w.risk_scores.overall_score:.1f}/100)" for w in top_works])

        context_str = f"Platform overview: {total} total projects ({completed} completed, {ongoing} ongoing). Risk distribution: {crit} Critical, {high} High. Top high-risk projects:\n{top_works_str}"
        base_answer = f"Hello! I am **Sentinel AI**, your virtual assistant. Currently, the system tracks **{total} projects** with **{crit} critical risk** cases flagged.\n\n### Top High-Risk Projects:\n{top_works_str}\n\nTry asking:\n- *\"Which project has the most fraud / highest risk?\"*\n- *\"Why is project PRJ000001 high risk?\"*\n- *\"Show delayed projects in Tamil Nadu.\"*\n- *\"Which agencies have unusually high cost deviations?\"*\n- *\"Summarize the latest document.\"*"

    # 1. Attempt Google Gemini API Generation if key configured
    from backend.app.nlp.gemini import query_gemini_api
    gemini_res = query_gemini_api(
        prompt=f"User Query: {query}\n\nGround-Truth Database Context:\n{context_str}\n\nPlease generate a clear, professional, data-rich answer for the platform dashboard user. If the user asks about fraud, highest risk, or delays, make sure to name the specific projects from the Ground-Truth Database Context.",
        system_prompt="You are Sentinel AI, an expert AI governance and fraud detection assistant for the MPLADS platform. ALWAYS ground your answers in the provided database context. Speak specifically, name project IDs and risk scores from the context. Do not make up project names or IDs."
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
