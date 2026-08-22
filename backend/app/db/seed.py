import random
import datetime
from sqlalchemy.orm import Session
from backend.app.models.models import (
    Base, Role, User, State, District, Agency, Work, Payment, Rule, RiskScore, Document, Alert, SystemSetting
)
from backend.app.core.security import get_password_hash
from backend.app.db.session import engine

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

    # 3. Seed States & Districts
    states_data = [
        {"code": "DL", "name": "Delhi", "districts": [{"code": "CD", "name": "Central Delhi"}, {"code": "ND", "name": "New Delhi"}]},
        {"code": "TN", "name": "Tamil Nadu", "districts": [{"code": "CH", "name": "Chennai"}, {"code": "CO", "name": "Coimbatore"}]},
        {"code": "MH", "name": "Maharashtra", "districts": [{"code": "MU", "name": "Mumbai"}, {"code": "PU", "name": "Pune"}]},
        {"code": "KA", "name": "Karnataka", "districts": [{"code": "BU", "name": "Bangalore Urban"}, {"code": "MY", "name": "Mysore"}]},
    ]

    for s_data in states_data:
        state = db.query(State).filter(State.code == s_data["code"]).first()
        if not state:
            state = State(code=s_data["code"], name=s_data["name"])
            db.add(state)
        
        for d_data in s_data["districts"]:
            district = db.query(District).filter(District.code == d_data["code"]).first()
            if not district:
                district = District(code=d_data["code"], name=d_data["name"], state_code=state.code)
                db.add(district)
    db.commit()

    # 4. Seed Agencies
    agencies_names = [
        ("Public Works Department (PWD)", "CH"),
        ("National Buildings Construction Corporation (NBCC)", "CH"),
        ("Central Public Works Department (CPWD)", "CD"),
        ("District Rural Development Agency (DRDA)", "CO"),
        ("Maharashtra State PWD", "MU"),
        ("Pune Municipal Corporation", "PU"),
        ("Bruhat Bengaluru Mahanagara Palike (BBMP)", "BU"),
        ("Mysore Urban Development Authority", "MY")
    ]

    db_agencies = []
    for name, dist_code in agencies_names:
        agency = db.query(Agency).filter(Agency.name == name).first()
        if not agency:
            agency = Agency(
                name=name,
                district_code=dist_code,
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

    # Refresh agencies from database to get their IDs
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

    # 6. Seed System Settings (Risk weights)
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
    db.commit()

    # 7. Seed 1000 Works (with deliberate anomalies)
    existing_works_count = db.query(Work).count()
    if existing_works_count >= 1000:
        print("Database already seeded with works.")
        return

    print("Seeding works and payments... This might take a few moments.")
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

    mps = [
        ("Shri Narendra Modi", "Varanasi", "DL", "CD"),
        ("Dr. S. Jaishankar", "Gujarat Rajya Sabha", "TN", "CH"),
        ("Smt. Nirmala Sitharaman", "Karnataka Rajya Sabha", "KA", "BU"),
        ("Shri Amit Shah", "Gandhinagar", "MH", "MU")
    ]

    base_lat_long = {
        "CD": (28.64, 77.22),
        "ND": (28.61, 77.20),
        "CH": (13.08, 80.27),
        "CO": (11.01, 76.95),
        "MU": (18.97, 72.82),
        "PU": (18.52, 73.85),
        "BU": (12.97, 77.59),
        "MY": (12.29, 76.63)
    }

    districts_in_db = db.query(District).all()
    district_list = [d.code for d in districts_in_db]

    today = datetime.date.today()

    works_to_add = []
    payments_to_add = []
    risk_scores_to_add = []

    # Generate 1010 works to be safe
    for i in range(1, 1011):
        work_id = f"MPLADS-{2026:04d}-{i:04d}"
        category = random.choice(categories)
        
        # Pick state/district
        d_code = random.choice(district_list)
        district_obj = db.query(District).filter(District.code == d_code).first()
        state_code = district_obj.state_code

        # Names
        block = f"Block-{random.randint(1, 5)}"
        village = f"Village-{random.randint(1, 20)}"
        
        desc_tmpl = random.choice(work_templates[category])
        description = desc_tmpl.format(village=village, block=block)

        # MP & Constituency
        mp_name, constituency, _, _ = random.choice(mps)
        
        # Coordinates
        base_lat, base_lon = base_lat_long.get(d_code, (13.0, 80.0))
        lat = base_lat + random.uniform(-0.08, 0.08)
        lon = base_lon + random.uniform(-0.08, 0.08)

        # Amounts
        estimated_cost = random.uniform(500000, 5000000) # 5L to 50L
        sanctioned_amount = estimated_cost * random.uniform(0.95, 1.05)

        # Dates
        days_ago = random.randint(30, 700)
        rec_date = today - datetime.timedelta(days=days_ago)
        sanc_date = rec_date + datetime.timedelta(days=random.randint(15, 60))
        
        expected_duration = random.randint(180, 360)
        exp_completion_date = sanc_date + datetime.timedelta(days=expected_duration)

        status_pool = ["Sanctioned", "Ongoing", "Completed"]
        status = random.choices(status_pool, weights=[15, 55, 30], k=1)[0]
        
        # Adjust ongoing works that are overdue to be ongoing or completed
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

        agency = random.choice(db_agencies)
        agency_id = agency.id

        # Flag fields for anomaly injection
        is_anomaly = False
        anomaly_type = None

        # Inject anomalies into approximately 15% of records
        if i % 7 == 0:
            is_anomaly = True
            r_val = random.randint(1, 7)
            if r_val == 1:
                # 1. Physical vs Financial Progress Mismatch
                status = "Ongoing"
                financial_progress = random.uniform(85.0, 95.0)
                physical_progress = random.uniform(20.0, 45.0)
                expenditure = sanctioned_amount * (financial_progress / 100.0)
                anomaly_type = "mismatch"
            elif r_val == 2:
                # 2. Cost Overrun
                status = "Completed"
                expenditure = sanctioned_amount * random.uniform(1.15, 1.45)
                physical_progress = 100.0
                financial_progress = 100.0
                anomaly_type = "cost_overrun"
            elif r_val == 3:
                # 3. Excessive Project Delay
                status = "Ongoing"
                sanc_date = today - datetime.timedelta(days=500)
                exp_completion_date = sanc_date + datetime.timedelta(days=180) # 180 days expected duration
                # Overdue by almost a year
                physical_progress = random.uniform(15.0, 40.0)
                financial_progress = physical_progress * random.uniform(0.9, 1.1)
                expenditure = sanctioned_amount * (financial_progress / 100.0)
                anomaly_type = "delay"
            elif r_val == 4:
                # 4. Low Utilization
                status = "Ongoing"
                sanc_date = today - datetime.timedelta(days=250)
                exp_completion_date = sanc_date + datetime.timedelta(days=365)
                financial_progress = random.uniform(0.0, 5.0)
                physical_progress = 0.0
                expenditure = sanctioned_amount * (financial_progress / 100.0)
                anomaly_type = "low_utilization"
            elif r_val == 5:
                # 5. Missing Critical Info
                lat = None
                lon = None
                anomaly_type = "missing_info"
            elif r_val == 6:
                # 6. Cost Anomaly (Comparable outliers - e.g. 10x normal cost)
                estimated_cost = random.uniform(8000000, 15000000) # 80L to 1.5Cr (Normal median is ~24L)
                sanctioned_amount = estimated_cost
                if status == "Completed":
                    expenditure = sanctioned_amount
                elif status == "Ongoing":
                    expenditure = sanctioned_amount * (financial_progress / 100.0)
                anomaly_type = "cost_anomaly"
            elif r_val == 7:
                # 7. Document mismatch
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
            # Inject suspicious payment burst: multiple payments in 5 days
            if anomaly_type == "mismatch" or (is_anomaly and random.random() < 0.3):
                # Suspicious: 3 payments of large amounts in a few days
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
                # Normal payment distribution
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
            # Match or mismatch PDF amount
            pdf_amount = sanctioned_amount
            consistency_score = 100.0
            doc_data = {
                "work_id": work_id,
                "project_name": description,
                "sanctioned_amount": sanctioned_amount,
                "sanction_date": sanc_date.strftime("%Y-%m-%d"),
                "agency": agency.name
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
                         f"Sanction Date: {doc_data['sanction_date']}. Implementing Agency: {agency.name}.",
                extracted_data=doc_data,
                consistency_score=consistency_score
            )
            db.add(doc)

    # Ingest Works in batch
    db.add_all(works_to_add)
    db.commit()

    # Ingest Payments in batch
    db.add_all(payments_to_add)
    db.commit()

    # Inject Duplicate works explicitly
    # We will inject 5 duplicate work groups (10 works total)
    duplicate_indices = [25, 120, 245, 450, 680]
    for d_idx in duplicate_indices:
        base_work = works_to_add[d_idx]
        dup_work_id = f"MPLADS-2026-DUP{d_idx}"
        
        # Similar description (93% similarity)
        dup_description = base_work.description.replace("Installation of", "Construction and setting up of")
        dup_description = dup_description.replace("Construction of", "Setting up and construction of")
        
        # Geographic coordinates close (1.2 km distance is roughly 0.01 degrees)
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

        # Add duplicate warning alert
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

    print("Synthesized works & payments successfully populated in the DB.")
