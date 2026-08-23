"""
MPLADS Sentinel AI — SIH 2026 Showcase Dataset Generator
=========================================================
Generates a fully-featured, self-consistent dataset anchored to the official
MP (2) [Lok Sabha] and MP (3) [Rajya Sabha] allocation CSV files.

Designed to demonstrate ALL platform features:
  1. Risk Monitor (diverse risk levels: Critical / High / Medium / Low)
  2. Root-Cause Backtracking (all 6 signal layers)
  3. Agency Intelligence (agency risk concentration patterns)
  4. Documents & OCR (domain-matched PDF for every project, with mismatches)
  5. Case Investigations (linked to flagged projects with evidence chain)
  6. Detection Rules (cost overrun, delay, fin-phys mismatch, duplicate payment)
  7. Overview Dashboard KPIs (anomalies, heatmap, trend)

Anomaly Scenarios (intentionally designed for demo):
  A. NORMAL                    — 50% of projects
  B. COST_OVERRUN              — 10% (expenditure > sanctioned amount)
  C. FIN_PHYS_MISMATCH         — 10% (90% funds spent, <20% physical progress)
  D. PROJECT_DELAY             — 10% (overdue > 6 months, stalled progress)
  E. DUPLICATE_PAYMENT         — 5%  (same vendor, same district, same amount ×2)
  F. DOCUMENT_MISMATCH         — 5%  (OCR extracted amount ≠ DB amount)
  G. VENDOR_COLLUSION          — 5%  (one vendor spans 8+ agencies)
  H. LOW_UTILIZATION           — 5%  (sanctioned 12+ months ago, <5% spent)
"""

import sys, os, random, datetime, json
import pandas as pd
import numpy as np

random.seed(2026)
np.random.seed(2026)

# ── Geographic constants ──────────────────────────────────────────────────────
STATES_INFO = [
    {"code": "MH", "name": "Maharashtra",      "lat": 19.7515, "lon": 75.7139},
    {"code": "TN", "name": "Tamil Nadu",        "lat": 11.1271, "lon": 78.6569},
    {"code": "UP", "name": "Uttar Pradesh",     "lat": 26.8467, "lon": 80.9462},
    {"code": "WB", "name": "West Bengal",       "lat": 22.9868, "lon": 87.8550},
    {"code": "BR", "name": "Bihar",             "lat": 25.0961, "lon": 85.3131},
    {"code": "KA", "name": "Karnataka",         "lat": 15.3173, "lon": 75.7139},
    {"code": "GJ", "name": "Gujarat",           "lat": 22.2587, "lon": 71.1924},
    {"code": "RJ", "name": "Rajasthan",         "lat": 27.0238, "lon": 74.2179},
    {"code": "KL", "name": "Kerala",            "lat":  8.5241, "lon": 76.9366},
    {"code": "PB", "name": "Punjab",            "lat": 31.1471, "lon": 75.3412},
    {"code": "HR", "name": "Haryana",           "lat": 29.0588, "lon": 76.0856},
    {"code": "DL", "name": "Delhi",             "lat": 28.6139, "lon": 77.2090},
    {"code": "MP", "name": "Madhya Pradesh",    "lat": 22.9734, "lon": 78.6569},
    {"code": "AP", "name": "Andhra Pradesh",    "lat": 15.9129, "lon": 79.7400},
    {"code": "TS", "name": "Telangana",         "lat": 18.1124, "lon": 79.0193},
    {"code": "OD", "name": "Odisha",            "lat": 20.9517, "lon": 85.0985},
    {"code": "AS", "name": "Assam",             "lat": 26.2006, "lon": 92.9376},
    {"code": "JK", "name": "Jammu & Kashmir",   "lat": 33.7782, "lon": 76.5762},
    {"code": "JH", "name": "Jharkhand",         "lat": 23.6102, "lon": 85.2799},
    {"code": "CG", "name": "Chhattisgarh",      "lat": 21.2787, "lon": 81.8661},
    {"code": "UK", "name": "Uttarakhand",       "lat": 30.0668, "lon": 79.0193},
    {"code": "HP", "name": "Himachal Pradesh",  "lat": 31.1048, "lon": 77.1734},
    {"code": "GA", "name": "Goa",               "lat": 15.2993, "lon": 74.1240},
    {"code": "MN", "name": "Manipur",           "lat": 24.6637, "lon": 93.9063},
    {"code": "MZ", "name": "Mizoram",           "lat": 23.1645, "lon": 92.9376},
    {"code": "SK", "name": "Sikkim",            "lat": 27.5330, "lon": 88.5122},
    {"code": "NL", "name": "Nagaland",          "lat": 26.1584, "lon": 94.5624},
    {"code": "TR", "name": "Tripura",           "lat": 23.9408, "lon": 91.9882},
]

DISTRICTS_PER_STATE = {
    "MH": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Thane"],
    "TN": ["Chennai", "Coimbatore", "Madurai", "Salem", "Tiruchirappalli", "Tirunelveli"],
    "UP": ["Lucknow", "Kanpur", "Varanasi", "Agra", "Allahabad", "Meerut"],
    "WB": ["Kolkata", "Howrah", "Darjeeling", "Siliguri", "Asansol", "Durgapur"],
    "BR": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Darbhanga", "Aurangabad"],
    "KA": ["Bengaluru", "Mysuru", "Hubballi", "Mangaluru", "Kalaburagi", "Belagavi"],
    "GJ": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Gandhinagar", "Bhavnagar"],
    "RJ": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Bikaner", "Ajmer"],
    "KL": ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur", "Kollam", "Alappuzha"],
    "PB": ["Amritsar", "Ludhiana", "Chandigarh", "Patiala", "Jalandhar", "Bathinda"],
    "HR": ["Gurugram", "Faridabad", "Panipat", "Ambala", "Hisar", "Rohtak"],
    "DL": ["New Delhi", "North Delhi", "South Delhi", "East Delhi", "West Delhi", "Central Delhi"],
    "MP": ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain", "Sagar"],
    "AP": ["Visakhapatnam", "Vijayawada", "Guntur", "Tirupati", "Nellore", "Kurnool"],
    "TS": ["Hyderabad", "Warangal", "Nizamabad", "Khammam", "Karimnagar", "Ramagundam"],
    "OD": ["Bhubaneswar", "Cuttack", "Puri", "Rourkela", "Sambalpur", "Berhampur"],
    "AS": ["Guwahati", "Dibrugarh", "Silchar", "Jorhat", "Nagaon", "Tezpur"],
    "JK": ["Srinagar", "Jammu", "Leh", "Anantnag", "Sopore", "Kathua"],
    "JH": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Hazaribagh", "Deoghar"],
    "CG": ["Raipur", "Bhilai", "Bilaspur", "Korba", "Durg", "Rajnandgaon"],
    "UK": ["Dehradun", "Haridwar", "Rishikesh", "Nainital", "Roorkee", "Mussoorie"],
    "HP": ["Shimla", "Dharamshala", "Mandi", "Solan", "Kullu", "Manali"],
    "GA": ["Panaji", "Margao", "Vasco", "Mapusa", "Ponda", "Calangute"],
    "MN": ["Imphal", "Churachandpur", "Thoubal", "Bishnupur", "Senapati", "Ukhrul"],
    "MZ": ["Aizawl", "Lunglei", "Champhai", "Serchhip", "Kolasib", "Mamit"],
    "SK": ["Gangtok", "Namchi", "Gyalshing", "Mangan", "Jorethang", "Rangpo"],
    "NL": ["Kohima", "Dimapur", "Mokokchung", "Wokha", "Zunheboto", "Phek"],
    "TR": ["Agartala", "Udaipur", "Dharmanagar", "Sabroom", "Belonia", "Khowai"],
}

# Showcase agency templates (each state gets 4 agencies for diversity)
AGENCY_TEMPLATES = [
    {"suffix": "Public Works Department (PWD)",               "risk_profile": "mixed"},
    {"suffix": "District Rural Development Agency (DRDA)",    "risk_profile": "high"},   # intentionally risky
    {"suffix": "Municipal Corporation Infrastructure Cell",   "risk_profile": "medium"},
    {"suffix": "State Water Supply & Sanitation Board (WSSB)","risk_profile": "low"},
]

CATEGORIES = [
    "WATER_SUPPLY", "SCHOOL_INFRASTRUCTURE", "HEALTHCARE",
    "ROAD_CONSTRUCTION", "SANITATION", "SOLAR_ENERGY",
    "COMMUNITY_HALL", "DRAINAGE", "PUBLIC_TOILET", "BUS_SHELTER",
    "ROAD_REPAIR", "BRIDGE", "SPORTS_FACILITY",
]

DESC_TEMPLATES = {
    "WATER_SUPPLY":          ["Installation of RO Drinking Water Plant at {loc}", "Borewell Drilling & Submersible Pump Supply at {loc}", "Overhead Water Tank Construction & Pipeline Network at {loc}"],
    "SCHOOL_INFRASTRUCTURE": ["Construction of Additional Classrooms at {loc} Government School", "Digital Smart Classroom & IT Lab Setup at {loc}", "School Boundary Wall & Sanitation Block at {loc}"],
    "HEALTHCARE":            ["Medical Equipment Procurement for {loc} PHC", "Maternity Ward Upgradation at {loc} District Hospital", "Ambulance Purchase for {loc} Health Centre"],
    "ROAD_CONSTRUCTION":     ["Bituminous Road Construction from {loc} to Panchayat HQ", "Concrete Village Connecting Road at {loc}", "Inter-village Link Road Construction at {loc}"],
    "SANITATION":            ["Community Toilet Complex at {loc} Market Area", "RCC Underground Sewage Network at {loc}", "Solid Waste Processing Plant at {loc}"],
    "SOLAR_ENERGY":          ["Solar High-Mast Street Lighting at {loc}", "Solar Micro-Grid for {loc} Village Power Supply", "Rooftop Solar Panel Installation at {loc} Government Building"],
    "COMMUNITY_HALL":        ["Multipurpose Community Hall at {loc}", "Panchayat Bhawan Construction at {loc}", "Village Auditorium & Public Address System at {loc}"],
    "DRAINAGE":              ["Storm Water Drain Construction at {loc}", "Covered Concrete Drain Network at {loc}", "Flood Control Channel at {loc}"],
    "PUBLIC_TOILET":         ["Public Sanitation Complex at {loc} Bus Stand", "Highway Toilet Block near {loc}", "Market Public Toilet Unit at {loc}"],
    "BUS_SHELTER":           ["Passenger Bus Waiting Shelter at {loc}", "Modern Steel Bus Canopy at {loc} Junction", "Village Bus Stand & Commuter Amenities at {loc}"],
    "ROAD_REPAIR":           ["Pothole Repair & Road Resurfacing at {loc}", "Bridge Deck Repair & Railing at {loc}", "Road Widening & Strengthening at {loc}"],
    "BRIDGE":                ["RCC Bridge Construction over {loc} River", "Footbridge for Villagers at {loc}", "Box Culvert Bridge at {loc} Nala"],
    "SPORTS_FACILITY":       ["Indoor Sports Hall at {loc}", "Children Playground Equipment at {loc} Park", "Multi-purpose Sports Ground Levelling at {loc}"],
}

VENDOR_BY_CAT = {
    "WATER_SUPPLY":          "AquaPure Water Systems & Drilling Corp",
    "SCHOOL_INFRASTRUCTURE": "TechLine IT & Lab Equipment Solutions Pvt Ltd",
    "HEALTHCARE":            "MedTech Healthcare Infrastructure Ltd",
    "ROAD_CONSTRUCTION":     "Apex Infracon & Highway Contractors",
    "SANITATION":            "CleanWater Sanitation & Drainage Works Pvt Ltd",
    "SOLAR_ENERGY":          "SunPower Renewable Energy Systems",
    "COMMUNITY_HALL":        "National Civic Infrastructure Developers",
    "DRAINAGE":              "UrbanDrain Civil Engineering Co",
    "PUBLIC_TOILET":         "SwachhBharat Sanitation Infra Ltd",
    "BUS_SHELTER":           "SmartTransit Urban Infra Solutions",
    "ROAD_REPAIR":           "Speedway Repair & Resurfacing Contractors",
    "BRIDGE":                "BridgeTech Structures Pvt Ltd",
    "SPORTS_FACILITY":       "ProSport Infrastructure & Turf Solutions",
}

# COLLUSION VENDOR — spans many agencies (intentional anomaly for showcase)
COLLUSION_VENDOR = "Paramount Multi-Sector Construction Ltd"

def generate_showcase_dataset():
    print("=== SIH 2026: Generating Showcase Dataset ===")

    # ── 1. Read Official MP CSVs ──────────────────────────────────────────────
    df2 = pd.read_csv("Dataset/Allocated Limit for Honble MPs (2).csv", header=None)
    df2_clean = df2.iloc[3:].copy()
    df2_clean.columns = ["sr_no", "state_ut", "mp_name", "constituency", "allocated_amount_inr"]

    df3 = pd.read_csv("Dataset/Allocated Limit for Honble MPs (3).csv", header=None)
    df3_clean = df3.iloc[2:].copy()
    df3_clean.columns = ["sr_no", "state_ut", "mp_name", "house_type", "allocated_amount_inr"]

    # Build MP master — one row per MP
    mp_rows = []
    for _, r in df2_clean.iterrows():
        st = str(r["state_ut"]).strip() if not pd.isna(r["state_ut"]) else "Maharashtra"
        name = str(r["mp_name"]).strip() if not pd.isna(r["mp_name"]) else "Hon'ble MP"
        const = str(r["constituency"]).strip() if not pd.isna(r["constituency"]) else st
        try:
            amt = float(str(r["allocated_amount_inr"]).replace(",", "").strip())
        except:
            amt = 147_000_000.0
        mp_rows.append({"mp_name": name, "state_ut": st, "constituency": const, "house": "Lok Sabha", "allocated_inr": amt})

    for _, r in df3_clean.iterrows():
        st = str(r["state_ut"]).strip() if not pd.isna(r["state_ut"]) else "Delhi"
        name = str(r["mp_name"]).strip() if not pd.isna(r["mp_name"]) else "Hon'ble MP"
        try:
            amt = float(str(r["allocated_amount_inr"]).replace(",", "").strip())
        except:
            amt = 49_000_000.0
        mp_rows.append({"mp_name": name, "state_ut": st, "constituency": f"{st} (RS)", "house": "Rajya Sabha", "allocated_inr": amt})

    print(f"  Loaded {len(mp_rows)} official MPs from CSV baselines.")

    # ── 2. Build state-to-MP lookup (limit to known states) ──────────────────
    state_name_to_code = {s["name"]: s["code"] for s in STATES_INFO}
    state_code_to_info = {s["code"]: s for s in STATES_INFO}

    # Normalise state names from CSV
    ST_ALIASES = {
        "Jammu And Kashmir": "Jammu & Kashmir",
        "Jammu and Kashmir": "Jammu & Kashmir",
        "Orissa": "Odisha",
        "Uttarakhand": "Uttarakhand",
        "Arunachal Pradesh": "Arunachal Pradesh",
        "Andaman & Nicobar": "Andaman & Nicobar",
    }

    for mp in mp_rows:
        name = ST_ALIASES.get(mp["state_ut"], mp["state_ut"])
        mp["state_code"] = state_name_to_code.get(name, None)

    # Keep only MPs from states we have coordinates for
    valid_mps = [m for m in mp_rows if m["state_code"] is not None]
    print(f"  {len(valid_mps)} MPs matched to mapped States/UTs.")

    # Sample to keep dataset medium-sized: target ~900 projects (3 per MP from sample)
    # Use up to 300 unique MPs
    sampled_mps = random.sample(valid_mps, min(300, len(valid_mps)))

    # ── 3. Build Agencies ─────────────────────────────────────────────────────
    agency_rows = []
    ag_id = 1
    state_agency_map = {}  # state_code -> list of agency row-dicts

    for st in STATES_INFO:
        sc = st["code"]
        districts = DISTRICTS_PER_STATE.get(sc, ["District HQ"])
        state_agency_map[sc] = []
        for tmpl in AGENCY_TEMPLATES:
            dist = random.choice(districts)
            ag_name = f"{dist} {tmpl['suffix']}"
            agency_rows.append({
                "entity_id": f"AGENCY_{ag_id:04d}",
                "entity_name": ag_name,
                "state_code": sc,
                "state_ut": st["name"],
                "district": dist,
                "entity_type": "Implementing Agency",
                "risk_profile": tmpl["risk_profile"],
            })
            state_agency_map[sc].append({"id": ag_id, "name": ag_name, "district": dist, "risk_profile": tmpl["risk_profile"]})
            ag_id += 1

    df_agencies = pd.DataFrame(agency_rows)
    df_agencies.to_csv("Dataset/entities.csv", index=False)
    df_agencies.to_csv("Dataset/entities_corrected.csv", index=False)
    print(f"  Generated {len(df_agencies)} agencies.")

    # ── 4. Generate Projects ──────────────────────────────────────────────────
    # Anomaly distribution (for showcase)
    ANOMALY_WEIGHTS = {
        "NORMAL":              0.45,
        "COST_OVERRUN":        0.10,
        "FIN_PHYS_MISMATCH":   0.10,
        "PROJECT_DELAY":       0.10,
        "DUPLICATE_PAYMENT":   0.06,
        "DOCUMENT_MISMATCH":   0.06,
        "VENDOR_COLLUSION":    0.07,
        "LOW_UTILIZATION":     0.06,
    }
    scenarios = list(ANOMALY_WEIGHTS.keys())
    weights   = list(ANOMALY_WEIGHTS.values())

    # HIGH-RISK AGENCY — deliberately seeds one agency with 80%+ anomaly rate
    # for agency-level backtracking showcase (pick first DRDA of MH)
    HIGH_RISK_AGENCY_NAME = "Mumbai District Rural Development Agency (DRDA)"

    proj_rows  = []
    fund_rows  = []
    doc_rows   = []

    proj_idx = 1
    txn_idx  = 1
    doc_idx  = 1

    base_date = datetime.date(2022, 4, 1)
    today     = datetime.date.today()

    # Track duplicate-payment pairs for showcase
    dup_pair_budget = 8   # how many duplicate pairs to generate

    for mp in sampled_mps:
        sc     = mp["state_code"]
        st_info = state_code_to_info[sc]
        cap_lat = st_info["lat"]
        cap_lon = st_info["lon"]
        districts = DISTRICTS_PER_STATE.get(sc, ["District HQ"])
        agencies  = state_agency_map.get(sc, [])
        if not agencies:
            continue

        n_projects = random.randint(2, 5)  # 2-5 projects per MP

        for k in range(n_projects):
            p_id    = f"PRJ{proj_idx:06d}"
            cat     = random.choice(CATEGORIES)
            dist    = random.choice(districts)
            loc_tag = f"{dist} Block-{k+1}"
            desc    = random.choice(DESC_TEMPLATES[cat]).format(loc=loc_tag)

            # Anomaly scenario
            scenario = random.choices(scenarios, weights=weights, k=1)[0]

            # Pick an agency — DRDA gets high-risk projects intentionally
            if scenario in ("COST_OVERRUN", "FIN_PHYS_MISMATCH", "VENDOR_COLLUSION") and agencies:
                drda_candidates = [a for a in agencies if "DRDA" in a["name"]]
                agency = drda_candidates[0] if drda_candidates else random.choice(agencies)
            else:
                agency = random.choice(agencies)

            agency_id   = agency["id"]
            agency_name = agency["name"]
            agency_dist = agency["district"]

            sanc_cost = round(random.uniform(500_000, 8_000_000), -4)
            est_cost  = sanc_cost

            # Dates
            start_d   = base_date + datetime.timedelta(days=random.randint(0, 600))
            sanc_d    = start_d + datetime.timedelta(days=random.randint(15, 45))

            # --- Scenario-specific values ---
            if scenario == "NORMAL":
                status      = random.choice(["Ongoing", "Ongoing", "Completed", "Sanctioned"])
                phys_prog   = 100.0 if status == "Completed" else round(random.uniform(20, 85), 1)
                exp_val     = sanc_cost if status == "Completed" else round(sanc_cost * phys_prog / 100, 2)
                exp_comp_d  = sanc_d + datetime.timedelta(days=random.randint(180, 365))
                act_comp_d  = exp_comp_d if status == "Completed" else None
                vendor      = VENDOR_BY_CAT.get(cat, "General Infrastructure Contractors")
                doc_amount  = sanc_cost  # consistent

            elif scenario == "COST_OVERRUN":
                status      = "Ongoing"
                overrun_pct = round(random.uniform(1.15, 1.55), 2)
                exp_val     = round(sanc_cost * overrun_pct, 2)  # EXCEEDS SANCTION
                phys_prog   = round(random.uniform(35, 70), 1)
                exp_comp_d  = sanc_d + datetime.timedelta(days=random.randint(180, 300))
                act_comp_d  = None
                vendor      = VENDOR_BY_CAT.get(cat, "General Infrastructure Contractors")
                doc_amount  = sanc_cost  # doc matches original, expenditure doesn't

            elif scenario == "FIN_PHYS_MISMATCH":
                status      = "Ongoing"
                phys_prog   = round(random.uniform(5, 20), 1)   # LOW PHYSICAL
                exp_val     = round(sanc_cost * random.uniform(0.80, 0.92), 2)  # HIGH FINANCIAL
                exp_comp_d  = sanc_d + datetime.timedelta(days=random.randint(180, 300))
                act_comp_d  = None
                vendor      = VENDOR_BY_CAT.get(cat, "General Infrastructure Contractors")
                doc_amount  = sanc_cost

            elif scenario == "PROJECT_DELAY":
                status      = "Ongoing"
                phys_prog   = round(random.uniform(10, 40), 1)
                exp_val     = round(sanc_cost * 0.45, 2)
                exp_comp_d  = base_date + datetime.timedelta(days=random.randint(60, 180))  # OVERDUE
                act_comp_d  = None
                vendor      = VENDOR_BY_CAT.get(cat, "General Infrastructure Contractors")
                doc_amount  = sanc_cost

            elif scenario == "DUPLICATE_PAYMENT":
                status      = "Ongoing"
                phys_prog   = round(random.uniform(30, 60), 1)
                exp_val     = round(sanc_cost * 0.75, 2)
                exp_comp_d  = sanc_d + datetime.timedelta(days=random.randint(180, 300))
                act_comp_d  = None
                vendor      = VENDOR_BY_CAT.get(cat, "General Infrastructure Contractors")
                doc_amount  = sanc_cost

            elif scenario == "DOCUMENT_MISMATCH":
                status      = "Ongoing"
                phys_prog   = round(random.uniform(20, 60), 1)
                exp_val     = round(sanc_cost * phys_prog / 100, 2)
                exp_comp_d  = sanc_d + datetime.timedelta(days=random.randint(180, 365))
                act_comp_d  = None
                vendor      = VENDOR_BY_CAT.get(cat, "General Infrastructure Contractors")
                doc_amount  = round(sanc_cost * random.uniform(1.10, 1.35), 2)  # INFLATED IN DOC

            elif scenario == "VENDOR_COLLUSION":
                status      = "Ongoing"
                phys_prog   = round(random.uniform(20, 50), 1)
                exp_val     = round(sanc_cost * phys_prog / 100, 2)
                exp_comp_d  = sanc_d + datetime.timedelta(days=random.randint(240, 400))
                act_comp_d  = None
                vendor      = COLLUSION_VENDOR   # SINGLE VENDOR across states
                doc_amount  = sanc_cost

            elif scenario == "LOW_UTILIZATION":
                status      = "Ongoing"
                phys_prog   = round(random.uniform(0, 5), 1)
                exp_val     = round(sanc_cost * random.uniform(0.01, 0.06), 2)  # BARELY SPENT
                sanc_d      = base_date + datetime.timedelta(days=random.randint(0, 90))  # Old sanction
                exp_comp_d  = sanc_d + datetime.timedelta(days=random.randint(180, 300))
                act_comp_d  = None
                vendor      = VENDOR_BY_CAT.get(cat, "General Infrastructure Contractors")
                doc_amount  = sanc_cost
            else:
                status = "Ongoing"; phys_prog = 50.0; exp_val = sanc_cost * 0.5; exp_comp_d = sanc_d + datetime.timedelta(days=300); act_comp_d = None; vendor = "General"; doc_amount = sanc_cost

            fin_prog = min(100.0, round(exp_val / sanc_cost * 100, 1)) if sanc_cost > 0 else phys_prog
            lat = round(cap_lat + random.uniform(-0.8, 0.8), 6)
            lon = round(cap_lon + random.uniform(-0.8, 0.8), 6)

            proj_rows.append({
                "project_id":                  p_id,
                "work_description":            desc,
                "work_category":               cat,
                "mp_name":                     mp["mp_name"],
                "mp_id":                       f"MP_{proj_idx:05d}",
                "constituency":                mp["constituency"],
                "state_ut":                    mp["state_ut"],
                "state_code":                  sc,
                "district":                    dist,
                "district_code":               f"{sc}_{dist.upper().replace(' ', '_')}",
                "block_or_urban":              f"Block-{k+1}",
                "village_or_locality":         f"Locality-{k+1}",
                "estimated_cost_inr":          est_cost,
                "sanctioned_cost_inr":         sanc_cost,
                "start_date":                  start_d.strftime("%Y-%m-%d"),
                "sanction_date":               sanc_d.strftime("%Y-%m-%d"),
                "expected_completion_date":    exp_comp_d.strftime("%Y-%m-%d"),
                "actual_completion_date":      act_comp_d.strftime("%Y-%m-%d") if act_comp_d else "",
                "status":                      status,
                "physical_completion_percentage": phys_prog,
                "implementing_agency_id":      f"AGENCY_{agency_id:04d}",
                "latitude":                    lat,
                "longitude":                   lon,
                "anomaly_scenario":            scenario,
            })

            # Fund transactions
            txn_date1 = sanc_d + datetime.timedelta(days=30)
            txn_date2 = sanc_d + datetime.timedelta(days=90)

            # Sanction transfer
            fund_rows.append({
                "transaction_id":    f"TRX{txn_idx:08d}",
                "project_id":        p_id,
                "mp_name":           mp["mp_name"],
                "transaction_type":  "SANCTION",
                "amount_inr":        sanc_cost,
                "transaction_date":  sanc_d.strftime("%Y-%m-%d"),
                "payment_mode":      "TREASURY_TRANSFER",
                "recipient_name":    agency_name,
            }); txn_idx += 1

            # 1st disbursement
            if exp_val > 0:
                p1 = round(exp_val * 0.55, 2)
                fund_rows.append({
                    "transaction_id":    f"TRX{txn_idx:08d}",
                    "project_id":        p_id,
                    "mp_name":           mp["mp_name"],
                    "transaction_type":  "EXPENDITURE",
                    "amount_inr":        p1,
                    "transaction_date":  txn_date1.strftime("%Y-%m-%d"),
                    "payment_mode":      "PFMS_E_PAYMENT",
                    "recipient_name":    vendor,
                }); txn_idx += 1

                # 2nd disbursement
                p2 = round(exp_val - p1, 2)
                fund_rows.append({
                    "transaction_id":    f"TRX{txn_idx:08d}",
                    "project_id":        p_id,
                    "mp_name":           mp["mp_name"],
                    "transaction_type":  "EXPENDITURE",
                    "amount_inr":        p2,
                    "transaction_date":  txn_date2.strftime("%Y-%m-%d"),
                    "payment_mode":      "PFMS_E_PAYMENT",
                    "recipient_name":    vendor,
                }); txn_idx += 1

                # DUPLICATE PAYMENT — extra transaction for showcase
                if scenario == "DUPLICATE_PAYMENT":
                    dup_date = txn_date1 + datetime.timedelta(days=random.randint(1, 5))
                    fund_rows.append({
                        "transaction_id":    f"TRX{txn_idx:08d}",
                        "project_id":        p_id,
                        "mp_name":           mp["mp_name"],
                        "transaction_type":  "EXPENDITURE",
                        "amount_inr":        p1,   # SAME amount as first payment!
                        "transaction_date":  dup_date.strftime("%Y-%m-%d"),
                        "payment_mode":      "PFMS_E_PAYMENT",
                        "recipient_name":    vendor,
                    }); txn_idx += 1

            # Purchase Bill Document (domain-matched)
            consistency = round(random.uniform(88, 98), 1) if scenario != "DOCUMENT_MISMATCH" else round(random.uniform(45, 72), 1)
            doc_rows.append({
                "document_id":         f"DOC{doc_idx:07d}",
                "project_id":          p_id,
                "document_type":       "PURCHASE_BILL",
                "vendor_name":         vendor,
                "category":            cat,
                "extracted_amount_inr":doc_amount,  # may differ for DOCUMENT_MISMATCH
                "sanctioned_amount_inr":sanc_cost,
                "consistency_score":   consistency,
                "mismatch_flag":       scenario == "DOCUMENT_MISMATCH",
                "file_name":           f"Purchase_Bill_{p_id}.pdf",
            }); doc_idx += 1

            # Utilization Certificate
            doc_rows.append({
                "document_id":         f"DOC{doc_idx:07d}",
                "project_id":          p_id,
                "document_type":       "UTILIZATION_CERTIFICATE",
                "vendor_name":         agency_name,
                "category":            cat,
                "extracted_amount_inr":round(exp_val, 2),
                "sanctioned_amount_inr":sanc_cost,
                "consistency_score":   round(random.uniform(90, 100), 1),
                "mismatch_flag":       False,
                "file_name":           f"Utilization_Certificate_{p_id}.pdf",
            }); doc_idx += 1

            proj_idx += 1

    df_projects = pd.DataFrame(proj_rows)
    df_projects.to_csv("Dataset/projects_corrected.csv", index=False)
    df_projects.to_csv("Dataset/projects.csv", index=False)
    print(f"  Generated {len(df_projects)} projects.")

    df_funds = pd.DataFrame(fund_rows)
    df_funds.to_csv("Dataset/fund_transactions_corrected.csv", index=False)
    df_funds.to_csv("Dataset/fund_transactions.csv", index=False)
    print(f"  Generated {len(df_funds)} fund transactions.")

    df_docs = pd.DataFrame(doc_rows)
    df_docs.to_csv("Dataset/documents_showcase.csv", index=False)
    print(f"  Generated {len(df_docs)} domain-matched documents.")

    # ── 5. Print Anomaly Summary ──────────────────────────────────────────────
    print("\n=== ANOMALY SCENARIO DISTRIBUTION ===")
    for sc_name, count in df_projects["anomaly_scenario"].value_counts().items():
        print(f"  {sc_name:30s}: {count} projects")

    print("\n=== DATASET GENERATION COMPLETE ===")
    return df_projects, df_funds, df_docs


if __name__ == "__main__":
    generate_showcase_dataset()
