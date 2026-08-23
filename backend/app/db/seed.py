import os
import csv
import random
import datetime
from sqlalchemy.orm import Session
from backend.app.models.models import (
    Base, Role, User, State, District, Agency, Work, Payment, Rule, RiskScore, Document, Alert, SystemSetting
)
from backend.app.core.security import get_password_hash
from backend.app.db.session import engine

STATE_CODES = {
    'Andaman And Nicobar Islands': 'AN', 'Andhra Pradesh': 'AP', 'Arunachal Pradesh': 'AR',
    'Assam': 'AS', 'Bihar': 'BR', 'Chandigarh': 'CH_UT', 'Chhattisgarh': 'CG',
    'Dadra And Nagar Haveli And Daman And Diu': 'DN', 'Delhi': 'DL', 'Goa': 'GA',
    'Gujarat': 'GJ', 'Haryana': 'HR', 'Himachal Pradesh': 'HP', 'Jammu And Kashmir': 'JK',
    'Jharkhand': 'JH', 'Karnataka': 'KA', 'Kerala': 'KL', 'Ladakh': 'LA',
    'Lakshadweep': 'LD', 'Madhya Pradesh': 'MP', 'Maharashtra': 'MH', 'Manipur': 'MN',
    'Meghalaya': 'ML', 'Mizoram': 'MZ', 'Nagaland': 'NL', 'Odisha': 'OD',
    'Puducherry': 'PY', 'Punjab': 'PB', 'Rajasthan': 'RJ', 'Sikkim': 'SK',
    'Tamil Nadu': 'TN', 'Telangana': 'TS', 'Tripura': 'TR', 'Uttar Pradesh': 'UP',
    'Uttarakhand': 'UK', 'West Bengal': 'WB'
}

STATE_GPS = {
    'AN': (11.62, 92.72), 'AP': (15.91, 79.74), 'AR': (28.21, 94.72), 'AS': (26.20, 92.93),
    'BR': (25.09, 85.31), 'CH_UT': (30.73, 76.77), 'CG': (21.27, 81.86), 'DN': (20.18, 73.01),
    'DL': (28.61, 77.20), 'GA': (15.29, 74.12), 'GJ': (22.25, 71.19), 'HP': (31.10, 77.17),
    'HR': (29.05, 76.08), 'JK': (33.77, 76.57), 'JH': (23.61, 85.27), 'KA': (15.31, 75.71),
    'KL': (10.85, 76.27), 'LA': (34.15, 77.57), 'LD': (10.56, 72.64), 'MP': (22.97, 78.65),
    'MH': (19.75, 75.71), 'MN': (24.66, 93.90), 'ML': (25.57, 91.89), 'MZ': (23.16, 92.83),
    'NL': (26.15, 94.56), 'OD': (20.95, 85.09), 'PY': (11.94, 79.80), 'PB': (31.14, 75.34),
    'RJ': (27.02, 74.21), 'SK': (27.53, 88.51), 'TN': (11.12, 78.65), 'TS': (18.11, 79.01),
    'TR': (23.94, 91.98), 'UP': (26.84, 80.94), 'UK': (30.06, 79.01), 'WB': (22.98, 87.85)
}

def load_real_mp_dataset():
    mps = []
    base_dir = os.getcwd()
    doc1 = os.path.join(base_dir, 'documents', 'Allocated Limit for Honble MPs (2).csv')
    doc2 = os.path.join(base_dir, 'documents', 'Allocated Limit for Honble MPs (3).csv')

    if os.path.exists(doc1):
        with open(doc1, mode='r', encoding='utf-8-sig', errors='ignore') as f:
            r = list(csv.reader(f))
            for row in r[3:]:
                if len(row) >= 5 and row[0].strip().isdigit():
                    state, name, const, amt = row[1].strip(), row[2].strip(), row[3].strip(), row[4].strip()
                    try:
                        amt_val = float(amt)
                    except:
                        amt_val = 147000000.0
                    st_code = STATE_CODES.get(state, state[:2].upper())
                    mps.append({
                        'name': name.title(),
                        'constituency': const.title(),
                        'state_name': state,
                        'state_code': st_code,
                        'allocated_amount': amt_val,
                        'type': 'Lok Sabha'
                    })

    if os.path.exists(doc2):
        with open(doc2, mode='r', encoding='utf-8-sig', errors='ignore') as f:
            r = list(csv.reader(f))
            for row in r[2:]:
                if len(row) >= 5 and row[0].strip().isdigit():
                    state, name, mp_type, amt = row[1].strip(), row[2].strip(), row[3].strip(), row[4].strip()
                    try:
                        amt_val = float(amt)
                    except:
                        amt_val = 147000000.0
                    st_code = STATE_CODES.get(state, state[:2].upper())
                    mps.append({
                        'name': name.title(),
                        'constituency': f'{state} ({mp_type})',
                        'state_name': state,
                        'state_code': st_code,
                        'allocated_amount': amt_val,
                        'type': mp_type
                    })

    # Fallback default if files not found
    if not mps:
        mps = [
            {'name': 'Shri Narendra Modi', 'constituency': 'Varanasi', 'state_name': 'Uttar Pradesh', 'state_code': 'UP', 'allocated_amount': 147000000.0, 'type': 'Lok Sabha'},
            {'name': 'Dr. S. Jaishankar', 'constituency': 'Gujarat Rajya Sabha', 'state_name': 'Gujarat', 'state_code': 'GJ', 'allocated_amount': 147000000.0, 'type': 'Rajya Sabha'},
            {'name': 'Smt. Nirmala Sitharaman', 'constituency': 'Karnataka Rajya Sabha', 'state_name': 'Karnataka', 'state_code': 'KA', 'allocated_amount': 147000000.0, 'type': 'Rajya Sabha'},
            {'name': 'Shri Amit Shah', 'constituency': 'Gandhinagar', 'state_name': 'Gujarat', 'state_code': 'GJ', 'allocated_amount': 147000000.0, 'type': 'Lok Sabha'}
        ]
    return mps

def seed_db(db: Session):
    # Create tables if not exist
    Base.metadata.create_all(bind=engine)

    # 1. Seed Roles
    roles = ["Ministry Administrator", "State Nodal Authority", "District Authority", "MP / Constituency Viewer", "Investigation Officer"]
    db_roles = []
    for r in roles:
        existing_role = db.query(Role).filter(Role.name == r).first()
        if not existing_role:
            db_role = Role(name=r)
            db.add(db_role)
            db_roles.append(db_role)
        else:
            db_roles.append(existing_role)
    db.commit()

    # Get role IDs
    role_map = {r.name: r.id for r in db.query(Role).all()}

    # 2. Seed Users
    users_data = [
        {"username": "admin", "password": "admin123", "role_id": role_map["Ministry Administrator"], "state": None, "district": None},
        {"username": "state_nodal", "password": "state123", "role_id": role_map["State Nodal Authority"], "state": "TN", "district": None},
        {"username": "district_auth", "password": "district123", "role_id": role_map["District Authority"], "state": "TN", "district": "CH"},
        {"username": "mp_viewer", "password": "mp123", "role_id": role_map["MP / Constituency Viewer"], "state": "TN", "district": "CH", "constituency": "Chennai South"},
        {"username": "investigator", "password": "investigator123", "role_id": role_map["Investigation Officer"], "state": None, "district": None},
    ]

    for u in users_data:
        existing_user = db.query(User).filter(User.username == u["username"]).first()
        if not existing_user:
            user = User(
                username=u["username"],
                hashed_password=get_password_hash(u["password"]),
                role_id=u["role_id"],
                state=u.get("state"),
                district=u.get("district"),
                constituency=u.get("constituency")
            )
            db.add(user)
    db.commit()

    # Load official MP dataset
    real_mps = load_real_mp_dataset()

    # 3. Seed States & Districts dynamically from real MP dataset
    states_dict = {}
    for m in real_mps:
        st_code = m['state_code']
        st_name = m['state_name']
        if st_code not in states_dict:
            states_dict[st_code] = {'name': st_name, 'constituencies': set()}
        states_dict[st_code]['constituencies'].add(m['constituency'])

    # Always ensure fallback legacy district codes exist for default demo accounts
    states_dict.setdefault("TN", {"name": "Tamil Nadu", "constituencies": set()})["constituencies"].add("Chennai")
    states_dict.setdefault("DL", {"name": "Delhi", "constituencies": set()})["constituencies"].add("Central Delhi")
    states_dict.setdefault("MH", {"name": "Maharashtra", "constituencies": set()})["constituencies"].add("Mumbai")
    states_dict.setdefault("KA", {"name": "Karnataka", "constituencies": set()})["constituencies"].add("Bangalore Urban")

    all_districts = []
    for st_code, st_info in states_dict.items():
        state_obj = db.query(State).filter(State.code == st_code).first()
        if not state_obj:
            state_obj = State(code=st_code, name=st_info['name'])
            db.add(state_obj)
            db.commit()

        for idx, const_name in enumerate(sorted(list(st_info['constituencies']))):
            d_code = f"{st_code}_{idx+1}"
            if const_name == "Chennai": d_code = "CH"
            elif const_name == "Central Delhi": d_code = "CD"
            elif const_name == "Mumbai": d_code = "MU"
            elif const_name == "Bangalore Urban": d_code = "BU"
            elif const_name == "Coimbatore": d_code = "CO"
            elif const_name == "Pune": d_code = "PU"
            elif const_name == "Mysore": d_code = "MY"
            elif const_name == "New Delhi": d_code = "ND"

            dist_obj = db.query(District).filter(District.code == d_code).first()
            if not dist_obj:
                dist_obj = District(code=d_code, name=const_name, state_code=st_code)
                db.add(dist_obj)
            all_districts.append(dist_obj)
    db.commit()

    # 4. Seed Agencies across districts
    agencies_templates = [
        "School Education Infrastructure Division",
        "District Rural Development Agency (DRDA)",
        "Public Works Department (PWD)",
        "Central Public Works Department (CPWD)",
        "Municipal Infrastructure Corporation",
        "State Water Supply & Sanitation Board",
        "District Health & Family Welfare Society",
        "Renewable Energy Development Agency (REDA)"
    ]

    db_agencies = []
    all_dists_in_db = db.query(District).all()
    for d in all_dists_in_db[:20]: # Distribute agencies across top districts
        for tmpl in agencies_templates:
            agency_name = f"{d.name} {tmpl}"
            agency = db.query(Agency).filter(Agency.name == agency_name).first()
            if not agency:
                agency = Agency(
                    name=agency_name,
                    district_code=d.code,
                    completion_rate=random.uniform(0.75, 0.95),
                    average_delay_days=random.uniform(30, 120),
                    average_cost_deviation=random.uniform(-0.05, 0.15),
                    risk_score=random.uniform(15, 45)
                )
                db.add(agency)
                db_agencies.append(agency)
            else:
                db_agencies.append(agency)
    db.commit()
    db_agencies = db.query(Agency).all()

    # 5. Seed Rules
    rules_data = [
        {"id": "RULE_DELAY", "name": "Excessive Project Delay", "description": "Flags works that exceed their expected completion date by more than 3 months.", "category": "Progress", "severity": "HIGH", "condition_expression": "work.status != 'Completed' and work.expected_completion_date and (today - work.expected_completion_date).days > 90", "threshold": 90.0},
        {"id": "RULE_FIN_PHYS_MISMATCH", "name": "Physical vs Financial Progress Mismatch", "description": "Flags works with high financial disbursement (> 80%) but low physical progress (< 50%).", "category": "Financial", "severity": "CRITICAL", "condition_expression": "work.financial_progress > 80.0 and work.physical_progress < 50.0", "threshold": 30.0},
        {"id": "RULE_COST_OVERRUN", "name": "Expenditure Cost Overrun", "description": "Flags works where actual expenditure exceeds sanctioned amount.", "category": "Financial", "severity": "CRITICAL", "condition_expression": "work.expenditure > work.sanctioned_amount", "threshold": 0.0},
        {"id": "RULE_LOW_UTILIZATION", "name": "Low Fund Utilization", "description": "Flags works with elapsed duration of >6 months but financial utilization is < 10%.", "category": "Financial", "severity": "MEDIUM", "condition_expression": "work.status == 'Ongoing' and work.financial_progress < 10.0 and work.sanction_date and (today - work.sanction_date).days > 180", "threshold": 180.0},
        {"id": "RULE_MISSING_INFO", "name": "Missing Critical Information", "description": "Flags works that are missing locations, sanction dates, or implementing agency IDs.", "category": "Compliance", "severity": "MEDIUM", "condition_expression": "work.latitude is None or work.longitude is None or work.sanction_date is None or work.implementing_agency_id is None", "threshold": 0.0},
        {"id": "RULE_PAYMENT_BURST", "name": "Suspicious Payment Timing", "description": "Flags works with multiple disbursements within a short period (concentration of funds).", "category": "Payment", "severity": "HIGH", "condition_expression": "payment_burst_detected(work)", "threshold": 5.0},
        {"id": "RULE_DOC_MISMATCH", "name": "Document Mismatch", "description": "Flags works where document-extracted values differ from database values.", "category": "Document", "severity": "HIGH", "condition_expression": "document_mismatch_detected(work)", "threshold": 0.0}
    ]

    for r in rules_data:
        existing_rule = db.query(Rule).filter(Rule.id == r["id"]).first()
        if not existing_rule:
            rule = Rule(**r)
            db.add(rule)
        else:
            existing_rule.name = r["name"]
            existing_rule.description = r["description"]
            existing_rule.category = r["category"]
            existing_rule.severity = r["severity"]
            existing_rule.condition_expression = r["condition_expression"]
            existing_rule.threshold = r["threshold"]
    db.commit()

    # 6. Seed System Settings (Risk weights & MP allocations)
    weights_setting = db.query(SystemSetting).filter(SystemSetting.key == "risk_weights").first()
    if not weights_setting:
        weights = SystemSetting(
            key="risk_weights",
            value={
                "financial_risk": 0.20,
                "delay_risk": 0.20,
                "cost_risk": 0.15,
                "duplicate_risk": 0.15,
                "payment_risk": 0.10,
                "compliance_risk": 0.10,
                "document_risk": 0.05,
                "geographic_risk": 0.05
            }
        )
        db.add(weights)

    mp_alloc_setting = db.query(SystemSetting).filter(SystemSetting.key == "mp_allocations").first()
    if not mp_alloc_setting:
        mp_alloc_data = {m['name']: m for m in real_mps}
        mp_alloc_setting = SystemSetting(
            key="mp_allocations",
            value=mp_alloc_data
        )
        db.add(mp_alloc_setting)
    db.commit()

    # 7. Seed Works, Payments, and Agencies dynamically from Dataset folder
    existing_works_count = db.query(Work).count()
    if existing_works_count >= 1000:
        print(f"Database already seeded with {existing_works_count} works.")
        return

    import pandas as pd
    dataset_dir = os.path.join(os.getcwd(), 'Dataset')
    
    proj_path = os.path.join(dataset_dir, 'projects_corrected.csv')
    if not os.path.exists(proj_path):
        proj_path = os.path.join(dataset_dir, 'projects.csv')
        
    fund_path = os.path.join(dataset_dir, 'fund_transactions_corrected.csv')
    if not os.path.exists(fund_path):
        fund_path = os.path.join(dataset_dir, 'fund_transactions.csv')
        
    ent_path = os.path.join(dataset_dir, 'entities_corrected.csv')
    if not os.path.exists(ent_path):
        ent_path = os.path.join(dataset_dir, 'entities.csv')
        
    geo_path = os.path.join(dataset_dir, 'geo_district.csv')
    
    if os.path.exists(proj_path):
        print(f"Ingesting dynamic dataset files from '{dataset_dir}'...")
        df_projects = pd.read_csv(proj_path)
        df_fund = pd.read_csv(fund_path) if os.path.exists(fund_path) else pd.DataFrame()
        df_entities = pd.read_csv(ent_path) if os.path.exists(ent_path) else pd.DataFrame()
        df_geo = pd.read_csv(geo_path) if os.path.exists(geo_path) else None

        def parse_date(d):
            if pd.isna(d) or not d or str(d).strip().lower() in ['nan', 'none', 'null', '']:
                return None
            try:
                return datetime.datetime.strptime(str(d).strip(), "%Y-%m-%d").date()
            except:
                return None

        # Seed States & Districts from Geo Districts
        state_map = {}
        dist_map = {}
        if df_geo is not None:
            for _, r in df_geo.iterrows():
                st_name = str(r['state_ut']).strip()
                st_code = STATE_CODES.get(st_name, st_name[:2].upper())
                d_name = str(r['district']).strip()
                d_code = f"{st_code}_{d_name.replace(' ', '_').upper()[:10]}"
                
                if st_code not in state_map:
                    st_obj = db.query(State).filter((State.code == st_code) | (State.name == st_name)).first()
                    if not st_obj:
                        st_obj = State(code=st_code, name=st_name)
                        db.add(st_obj)
                        db.commit()
                    state_map[st_code] = st_obj
                    st_code = st_obj.code
                    
                if d_code not in dist_map:
                    dist_obj = db.query(District).filter(District.code == d_code).first()
                    if not dist_obj:
                        dist_obj = District(code=d_code, name=d_name, state_code=st_code)
                        db.add(dist_obj)
                        db.commit()
                    dist_map[d_code] = dist_obj

        # Seed Agencies from Entities
        agencies_to_add = []
        for idx, r in df_entities.iterrows():
            raw_ent_id = str(r['entity_id']).strip() if not pd.isna(r['entity_id']) else ""
            try:
                ent_id = int(raw_ent_id.split('_')[-1])
            except:
                ent_id = idx + 1
            ent_name = str(r['entity_name']).strip()
            st_name = str(r.get('state_ut', '')).strip()
            st_code = STATE_CODES.get(st_name, st_name[:2].upper()) if st_name else 'DEF'
            d_name = str(r.get('district', '')).strip()
            d_code = f"{st_code}_{d_name.replace(' ', '_').upper()[:10]}" if d_name else None
            
            agency = db.query(Agency).filter(Agency.id == ent_id).first()
            if not agency:
                agency = Agency(
                    id=ent_id,
                    name=ent_name,
                    district_code=d_code,
                    completion_rate=0.85,
                    average_delay_days=45.0,
                    average_cost_deviation=0.05,
                    risk_score=25.0
                )
                agencies_to_add.append(agency)
        if agencies_to_add:
            db.add_all(agencies_to_add)
            db.commit()

        # Seed Works
        exp_by_proj = df_fund[df_fund['transaction_type'].isin(['EXPENDITURE', 'PAYMENT'])].groupby('project_id')['amount_inr'].sum().to_dict() if not df_fund.empty else {}

        works_to_add = []
        existing_work_ids = set(w[0] for w in db.query(Work.id).all())

        for _, r in df_projects.iterrows():
            p_id = str(r['project_id']).strip()
            if p_id in existing_work_ids:
                continue
                
            desc = str(r['work_description']).strip() if not pd.isna(r['work_description']) else "MPLADS Infrastructure Project"
            cat = str(r['work_category']).strip() if not pd.isna(r['work_category']) else "General Infrastructure"
            mp_id = str(r['mp_id']).strip() if not pd.isna(r['mp_id']) else "MP_001"
            const = str(r['constituency']).strip() if not pd.isna(r['constituency']) else "Constituency"
            st_name = str(r['state_ut']).strip() if not pd.isna(r['state_ut']) else "Delhi"
            st_code = STATE_CODES.get(st_name, st_name[:2].upper())
            d_name = str(r['district']).strip() if not pd.isna(r['district']) else "District"
            d_code = f"{st_code}_{d_name.replace(' ', '_').upper()[:10]}"
            
            if st_code not in state_map:
                st_obj = db.query(State).filter((State.code == st_code) | (State.name == st_name)).first()
                if not st_obj:
                    st_obj = State(code=st_code, name=st_name)
                    db.add(st_obj)
                    db.commit()
                state_map[st_code] = st_obj
                st_code = st_obj.code
                
            if d_code not in dist_map:
                d_obj = db.query(District).filter(District.code == d_code).first()
                if not d_obj:
                    d_obj = District(code=d_code, name=d_name, state_code=st_code)
                    db.add(d_obj)
                    db.commit()
                dist_map[d_code] = d_obj
                
            sanc_cost = float(r['sanctioned_cost_inr']) if not pd.isna(r['sanctioned_cost_inr']) else 1000000.0
            est_cost = float(r['estimated_cost_inr']) if not pd.isna(r['estimated_cost_inr']) else sanc_cost
            
            status_val = str(r['status']).strip().title() if not pd.isna(r['status']) else "Ongoing"
            if status_val == "Completed": status = "Completed"
            elif status_val == "Ongoing": status = "Ongoing"
            elif status_val == "Sanctioned": status = "Sanctioned"
            else: status = "Ongoing"
            
            phys_prog = float(r['physical_completion_percentage']) if not pd.isna(r['physical_completion_percentage']) else 0.0
            
            exp_val = float(exp_by_proj.get(p_id, 0.0))
            if exp_val == 0.0 and status == "Completed":
                exp_val = sanc_cost
            elif exp_val == 0.0 and status == "Ongoing":
                exp_val = sanc_cost * (phys_prog / 100.0)
                
            fin_prog = (exp_val / sanc_cost * 100.0) if sanc_cost > 0 else phys_prog
            fin_prog = min(100.0, max(0.0, fin_prog))
            
            raw_agency_id = str(r['implementing_agency_id']).strip() if not pd.isna(r['implementing_agency_id']) else ""
            try:
                agency_id = int(raw_agency_id.split('_')[-1])
            except:
                agency_id = None

            work = Work(
                id=p_id,
                description=desc,
                category=cat,
                work_type="Infrastructure",
                mp_name=f"Hon'ble MP ({mp_id})",
                constituency=const,
                state_code=st_code,
                district_code=d_code,
                block=str(r.get('block_or_urban', 'Block')).strip(),
                village=str(r.get('village_or_locality', 'Village')).strip(),
                latitude=float(r['latitude']) if not pd.isna(r['latitude']) else None,
                longitude=float(r['longitude']) if not pd.isna(r['longitude']) else None,
                recommendation_date=parse_date(r.get('start_date')),
                sanction_date=parse_date(r.get('sanction_date')),
                expected_completion_date=parse_date(r.get('expected_completion_date')),
                actual_completion_date=parse_date(r.get('actual_completion_date')),
                status=status,
                implementing_agency_id=agency_id,
                estimated_cost=est_cost,
                sanctioned_amount=sanc_cost,
                expenditure=exp_val,
                physical_progress=phys_prog,
                financial_progress=fin_prog
            )
            works_to_add.append(work)

        batch_size = 1000
        for i in range(0, len(works_to_add), batch_size):
            db.add_all(works_to_add[i:i+batch_size])
            db.commit()

        # Seed Payments
        if not df_fund.empty:
            payments_to_add = []
            existing_txn_refs = set(p[0] for p in db.query(Payment.transaction_ref).filter(Payment.transaction_ref.isnot(None)).all())
            
            for _, r in df_fund.iterrows():
                txn_id = str(r['transaction_id']).strip()
                if txn_id in existing_txn_refs:
                    continue
                    
                p_id = str(r['project_id']).strip()
                amt = float(r['amount_inr']) if not pd.isna(r['amount_inr']) else 0.0
                p_date = parse_date(r.get('transaction_date')) or datetime.date.today()
                p_type = str(r.get('transaction_type', 'Milestone')).strip().title()
                
                payment = Payment(
                    work_id=p_id,
                    payment_date=p_date,
                    amount=amt,
                    payment_type=p_type,
                    transaction_ref=txn_id
                )
                payments_to_add.append(payment)

            for i in range(0, len(payments_to_add), batch_size):
                db.add_all(payments_to_add[i:i+batch_size])
                db.commit()

        print(f"Dynamically populated DB with {len(works_to_add)} projects and {len(payments_to_add)} transactions from Dataset folder.")

        # ── Seed Domain-Matched Documents (showcase CSV if available) ──────────
        print("Seeding domain-matched official documents...")
        docs_to_add = []
        existing_doc_works = set(d[0] for d in db.query(Document.work_id).filter(Document.work_id.isnot(None)).all())

        # Prefer showcase CSV (has mismatch flags & domain-matched amounts)
        doc_csv = os.path.join(dataset_dir, "documents_showcase.csv")
        if os.path.exists(doc_csv):
            df_docs_showcase = pd.read_csv(doc_csv)
            for _, rd in df_docs_showcase.iterrows():
                p_id = str(rd["project_id"]).strip()
                doc_type = str(rd["document_type"]).strip()
                vendor   = str(rd["vendor_name"]).strip()
                cat      = str(rd["category"]).strip()
                ext_amt  = float(rd["extracted_amount_inr"]) if not pd.isna(rd["extracted_amount_inr"]) else 0.0
                sanc_amt = float(rd["sanctioned_amount_inr"]) if not pd.isna(rd["sanctioned_amount_inr"]) else ext_amt
                score    = float(rd["consistency_score"])    if not pd.isna(rd["consistency_score"])    else 95.0
                mismatch = bool(rd["mismatch_flag"])         if not pd.isna(rd["mismatch_flag"])        else False
                fname    = str(rd["file_name"]).strip()

                # Domain-matched OCR text
                if mismatch:
                    ocr_text = (
                        f"PURCHASE INVOICE (DOCUMENT) — Work ID: {p_id}.\n"
                        f"Vendor: {vendor}.\n"
                        f"INVOICE AMOUNT: Rs. {ext_amt:,.2f}.\n"
                        f"[ALERT: Amount deviates from DB Sanctioned Amount of Rs. {sanc_amt:,.2f}]"
                    )
                else:
                    ocr_text = (
                        f"OFFICIAL PURCHASE INVOICE — Work ID: {p_id}.\n"
                        f"Category: {cat}. Vendor: {vendor}.\n"
                        f"Sanctioned Amount: Rs. {sanc_amt:,.2f}. Invoice Amount: Rs. {ext_amt:,.2f}."
                    )

                docs_to_add.append(Document(
                    work_id=p_id,
                    file_name=fname,
                    document_type=doc_type,
                    file_path=f"documents/{fname}",
                    consistency_score=score,
                    ocr_text=ocr_text,
                    extracted_data={
                        "work_id": p_id,
                        "vendor": vendor,
                        "sanctioned_amount": sanc_amt,
                        "extracted_amount":  ext_amt,
                        "category": cat,
                        "mismatch": mismatch,
                    }
                ))
        else:
            # Fallback: auto-generate domain-matched docs for all works
            all_works = db.query(Work).all()
            for w in all_works:
                if w.id in existing_doc_works:
                    continue
                cat = (w.category or "").upper()
                VENDOR_MAP = {
                    "WATER_SUPPLY": "AquaPure Water Systems & Drilling Corp",
                    "SCHOOL_INFRASTRUCTURE": "TechLine IT & Lab Equipment Solutions Pvt Ltd",
                    "HEALTHCARE": "MedTech Healthcare Infrastructure Ltd",
                    "ROAD_CONSTRUCTION": "Apex Infracon & Highway Contractors",
                    "SANITATION": "CleanWater Sanitation & Drainage Works",
                    "SOLAR_ENERGY": "SunPower Renewable Energy Systems",
                    "COMMUNITY_HALL": "National Civic Infrastructure Developers",
                }
                v_name = VENDOR_MAP.get(cat, "National Civic Infrastructure Developers")
                docs_to_add.append(Document(
                    work_id=w.id,
                    file_name=f"Purchase_Bill_{w.id}.pdf",
                    document_type="PURCHASE_BILL",
                    file_path=f"documents/Purchase_Bill_{w.id}.pdf",
                    consistency_score=round(random.uniform(88.0, 98.0), 1),
                    ocr_text=f"OFFICIAL PURCHASE INVOICE — Work: {w.id}. Vendor: {v_name}. Amount: Rs. {w.sanctioned_amount:,.2f}.",
                    extracted_data={"work_id": w.id, "vendor": v_name, "sanctioned_amount": w.sanctioned_amount, "category": w.category}
                ))

        for i in range(0, len(docs_to_add), batch_size):
            db.add_all(docs_to_add[i:i+batch_size])
            db.commit()

        print(f"Seeded {len(docs_to_add)} domain-matched documents (mismatch-aware).")
