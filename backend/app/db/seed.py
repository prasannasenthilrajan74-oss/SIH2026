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
        "Public Works Department (PWD)",
        "District Rural Development Agency (DRDA)",
        "Central Public Works Department (CPWD)",
        "Municipal Infrastructure Corporation",
        "State Water Supply & Sanitation Board",
        "National Buildings Construction Corporation (NBCC)"
    ]

    db_agencies = []
    all_dists_in_db = db.query(District).all()
    for d in all_dists_in_db[:20]: # Distribute agencies across top districts
        agency_name = f"{d.name} {random.choice(agencies_templates)}"
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

    # 7. Seed 1000 Works (with real MP attributes & deliberate anomalies)
    existing_works_count = db.query(Work).count()
    if existing_works_count >= 1000:
        print("Database already seeded with works.")
        return

    print(f"Seeding 1,000+ works using official dataset of {len(real_mps)} Members of Parliament...")
    categories = [
        "Drinking Water", "Education", "Health & Family Welfare", 
        "Roads, Pathways and Bridges", "Sanitation & Public Health", 
        "Sports Facilities", "Electricity & Non-Conventional Energy"
    ]
    work_templates = {
        "Drinking Water": [
            "Installation of Hand Pump in {village}",
            "Construction of Water Tank and Pipeline at {village}",
            "R.O. Drinking Water Plant installation in {block} Block"
        ],
        "Education": [
            "Construction of Additional Classrooms at Govt School, {village}",
            "Supply of computers and laboratory equipments to High School, {block}",
            "Renovation of School library in {village}"
        ],
        "Health & Family Welfare": [
            "Construction of Primary Health Centre Subcentre, {village}",
            "Providing medical equipments for PHC in {block}",
            "Construction of maternity ward at Govt Hospital, {block}"
        ],
        "Roads, Pathways and Bridges": [
            "Concreting of Village Link Road in {village}",
            "Construction of culvert bridge on {village} main pathway",
            "Metal Tarring of road from {village} to {block}"
        ],
        "Sanitation & Public Health": [
            "Construction of Community Sanitary Complex in {village}",
            "Construction of stormwater drains in {village} street",
            "Public toilet installation near {block} bus stand"
        ],
        "Sports Facilities": [
            "Development of playground and fencing at {village}",
            "Construction of indoor gymnasium at sports club, {block}",
            "Supply of sports gear and youth club infrastructure in {village}"
        ],
        "Electricity & Non-Conventional Energy": [
            "Installation of Solar Street Lights in {village}",
            "Providing Solar Power Backups for Govt Buildings, {block}",
            "Extension of electricity line in Dalit Habitation, {village}"
        ]
    }

    today = datetime.date.today()
    works_to_add = []
    payments_to_add = []

    for i in range(1, 1011):
        work_id = f"MPLADS-{2026:04d}-{i:04d}"
        category = random.choice(categories)
        
        # Pick real MP
        real_mp = random.choice(real_mps)
        mp_name = real_mp['name']
        constituency = real_mp['constituency']
        state_code = real_mp['state_code']

        # Find matching district for state
        state_dists = db.query(District).filter(District.state_code == state_code).all()
        if state_dists:
            district_obj = random.choice(state_dists)
            d_code = district_obj.code
        else:
            d_code = "CH"

        block = f"Block-{random.randint(1, 5)}"
        village = f"Village-{random.randint(1, 20)}"
        
        desc_tmpl = random.choice(work_templates[category])
        description = desc_tmpl.format(village=village, block=block)

        # GPS Coordinates centered around state
        base_lat, base_lon = STATE_GPS.get(state_code, (13.08, 80.27))
        lat = base_lat + random.uniform(-0.4, 0.4)
        lon = base_lon + random.uniform(-0.4, 0.4)

        # Amounts
        estimated_cost = random.uniform(500000, 4500000) # 5L to 45L
        sanctioned_amount = estimated_cost * random.uniform(0.95, 1.05)

        # Dates
        days_ago = random.randint(30, 700)
        rec_date = today - datetime.timedelta(days=days_ago)
        sanc_date = rec_date + datetime.timedelta(days=random.randint(15, 60))
        
        expected_duration = random.randint(180, 360)
        exp_completion_date = sanc_date + datetime.timedelta(days=expected_duration)

        status_pool = ["Sanctioned", "Ongoing", "Completed"]
        status = random.choices(status_pool, weights=[15, 55, 30], k=1)[0]
        
        actual_comp_date = None
        if status == "Completed":
            actual_comp_date = exp_completion_date + datetime.timedelta(days=random.randint(-30, 180))
            if actual_comp_date > today:
                actual_comp_date = today - datetime.timedelta(days=random.randint(1, 15))
            physical_progress = 100.0
            financial_progress = 100.0
            expenditure = sanctioned_amount
        elif status == "Ongoing":
            physical_progress = random.uniform(10.0, 95.0)
            financial_progress = physical_progress * random.uniform(0.9, 1.1)
            financial_progress = min(100.0, max(0.0, financial_progress))
            expenditure = sanctioned_amount * (financial_progress / 100.0)
        else: # Sanctioned
            physical_progress = 0.0
            financial_progress = 0.0
            expenditure = 0.0

        agency = random.choice(db_agencies) if db_agencies else None
        agency_id = agency.id if agency else None

        # Inject anomalies into approximately 15% of records
        is_anomaly = False
        anomaly_type = None

        if i % 7 == 0:
            is_anomaly = True
            r_val = random.randint(1, 7)
            if r_val == 1:
                status = "Ongoing"
                financial_progress = random.uniform(85.0, 95.0)
                physical_progress = random.uniform(20.0, 45.0)
                expenditure = sanctioned_amount * (financial_progress / 100.0)
                anomaly_type = "mismatch"
            elif r_val == 2:
                status = "Completed"
                expenditure = sanctioned_amount * random.uniform(1.15, 1.45)
                physical_progress = 100.0
                financial_progress = 100.0
                anomaly_type = "cost_overrun"
            elif r_val == 3:
                status = "Ongoing"
                sanc_date = today - datetime.timedelta(days=500)
                exp_completion_date = sanc_date + datetime.timedelta(days=180)
                physical_progress = random.uniform(15.0, 40.0)
                financial_progress = physical_progress * random.uniform(0.9, 1.1)
                expenditure = sanctioned_amount * (financial_progress / 100.0)
                anomaly_type = "delay"
            elif r_val == 4:
                status = "Ongoing"
                sanc_date = today - datetime.timedelta(days=250)
                exp_completion_date = sanc_date + datetime.timedelta(days=365)
                financial_progress = random.uniform(0.0, 5.0)
                physical_progress = 0.0
                expenditure = sanctioned_amount * (financial_progress / 100.0)
                anomaly_type = "low_utilization"
            elif r_val == 5:
                lat = None
                lon = None
                anomaly_type = "missing_info"
            elif r_val == 6:
                estimated_cost = random.uniform(8000000, 15000000)
                sanctioned_amount = estimated_cost
                if status == "Completed":
                    expenditure = sanctioned_amount
                elif status == "Ongoing":
                    expenditure = sanctioned_amount * (financial_progress / 100.0)
                anomaly_type = "cost_anomaly"
            elif r_val == 7:
                anomaly_type = "doc_mismatch"

        work = Work(
            id=work_id,
            description=description,
            category=category,
            work_type="Infrastructure",
            mp_name=mp_name,
            constituency=constituency,
            state_code=state_code,
            district_code=d_code,
            block=block,
            village=village,
            latitude=lat,
            longitude=lon,
            recommendation_date=rec_date,
            sanction_date=sanc_date,
            expected_completion_date=exp_completion_date,
            actual_completion_date=actual_comp_date,
            status=status,
            implementing_agency_id=agency_id,
            estimated_cost=estimated_cost,
            sanctioned_amount=sanctioned_amount,
            expenditure=expenditure,
            physical_progress=physical_progress,
            financial_progress=financial_progress
        )
        works_to_add.append(work)

        # Generate Payments for works
        if expenditure > 0:
            num_payments = random.randint(1, 4)
            if anomaly_type == "mismatch" or (is_anomaly and random.random() < 0.3):
                p_date = sanc_date + datetime.timedelta(days=random.randint(10, 30))
                for p_idx in range(3):
                    payment = Payment(
                        work_id=work_id,
                        payment_date=p_date + datetime.timedelta(days=random.randint(0, 4)),
                        amount=(expenditure / 3) * random.uniform(0.95, 1.05),
                        payment_type="Milestone",
                        transaction_ref=f"TXN-{work_id}-{p_idx}-{random.randint(1000, 9999)}"
                    )
                    payments_to_add.append(payment)
            else:
                remaining_exp = expenditure
                for p_idx in range(num_payments):
                    p_amt = remaining_exp / (num_payments - p_idx)
                    p_amt = p_amt * random.uniform(0.9, 1.1)
                    if p_amt > remaining_exp or p_idx == num_payments - 1:
                        p_amt = remaining_exp
                    
                    p_date = sanc_date + datetime.timedelta(days=int((expected_duration / num_payments) * (p_idx + 1) * random.uniform(0.8, 1.1)))
                    if p_date > today:
                        p_date = today - datetime.timedelta(days=random.randint(1, 10))

                    payment = Payment(
                        work_id=work_id,
                        payment_date=p_date,
                        amount=p_amt,
                        payment_type="Advance" if p_idx == 0 else ("Final" if p_idx == num_payments - 1 else "Milestone"),
                        transaction_ref=f"TXN-{work_id}-{p_idx}-{random.randint(1000, 9999)}"
                    )
                    payments_to_add.append(payment)
                    remaining_exp -= p_amt
                    if remaining_exp <= 0:
                        break

        # Generate Document Metadata
        if sanc_date is not None:
            pdf_amount = sanctioned_amount
            consistency_score = 100.0
            doc_agency_name = agency.name if agency else "PWD"
            doc_data = {
                "work_id": work_id,
                "project_name": description,
                "sanctioned_amount": sanctioned_amount,
                "sanction_date": sanc_date.strftime("%Y-%m-%d"),
                "agency": doc_agency_name
            }
            if anomaly_type == "doc_mismatch":
                pdf_amount = sanctioned_amount * random.choice([1.2, 0.8, 1.5])
                consistency_score = 72.0
                doc_data["sanctioned_amount"] = pdf_amount
                doc_data["sanction_date"] = (sanc_date - datetime.timedelta(days=30)).strftime("%Y-%m-%d")

            doc = Document(
                work_id=work_id,
                document_type="Sanction Order",
                file_name=f"SanctionOrder_{work_id}.pdf",
                file_path=f"documents/{work_id}_sanction.pdf",
                ocr_text=f"Government of India. Sanction Order for Work ID: {work_id}. "
                         f"Project Name: {description}. Sanctioned Amount: Rs.{pdf_amount:,.2f}. "
                         f"Sanction Date: {doc_data['sanction_date']}. Implementing Agency: {doc_agency_name}.",
                extracted_data=doc_data,
                consistency_score=consistency_score
            )
            db.add(doc)

    db.add_all(works_to_add)
    db.commit()

    db.add_all(payments_to_add)
    db.commit()

    # Inject Duplicate works explicitly
    duplicate_indices = [25, 120, 245, 450, 680]
    for d_idx in duplicate_indices:
        base_work = works_to_add[d_idx]
        dup_work_id = f"MPLADS-2026-DUP{d_idx}"
        
        dup_description = base_work.description.replace("Installation of", "Construction and setting up of")
        dup_description = dup_description.replace("Construction of", "Setting up and construction of")
        
        lat = base_work.latitude + 0.008 if base_work.latitude else 13.08
        lon = base_work.longitude + 0.008 if base_work.longitude else 80.27

        dup_work = Work(
            id=dup_work_id,
            description=dup_description,
            category=base_work.category,
            work_type=base_work.work_type,
            mp_name=base_work.mp_name,
            constituency=base_work.constituency,
            state_code=base_work.state_code,
            district_code=base_work.district_code,
            block=base_work.block,
            village=base_work.village,
            latitude=lat,
            longitude=lon,
            recommendation_date=base_work.recommendation_date + datetime.timedelta(days=random.randint(-5, 5)),
            sanction_date=base_work.sanction_date + datetime.timedelta(days=random.randint(-5, 5)),
            expected_completion_date=base_work.expected_completion_date,
            status=base_work.status,
            implementing_agency_id=base_work.implementing_agency_id,
            estimated_cost=base_work.estimated_cost * random.uniform(0.98, 1.02),
            sanctioned_amount=base_work.sanctioned_amount * random.uniform(0.98, 1.02),
            expenditure=base_work.expenditure * random.uniform(0.98, 1.02),
            physical_progress=base_work.physical_progress,
            financial_progress=base_work.financial_progress
        )
        db.add(dup_work)
        db.commit()

        alert = Alert(
            work_id=dup_work_id,
            alert_type="DUP_WORK",
            severity="CRITICAL",
            score=94.0,
            reason=f"Suspiciously high similarity (94%) with work {base_work.id} in close proximity ({1.2:.1f} km). Same category, MP and district.",
            evidence={"duplicate_work_id": base_work.id, "distance_km": 1.2, "description_similarity": 0.94}
        )
        db.add(alert)
        db.commit()

    print(f"Synthesized 1,000+ works using {len(real_mps)} official MP dataset entries successfully populated in the DB.")
