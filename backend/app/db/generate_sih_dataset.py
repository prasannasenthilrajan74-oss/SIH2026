import sys
import os
import random
import datetime
import pandas as pd
import numpy as np

# Set random seed for reproducible, high-quality SIH dataset generation
random.seed(42)
np.random.seed(42)

def generate_dataset():
    print("=== SIH 2026: Generating Official Ground-Truth Dataset anchored to MP (2) & MP (3) ===")
    
    # 1. Read MP (2) - Lok Sabha MPs
    df_mp2 = pd.read_csv('Dataset/Allocated Limit for Honble MPs (2).csv', header=None)
    df_mp2_clean = df_mp2.iloc[3:].copy()
    df_mp2_clean.columns = ['sr_no', 'state_ut', 'mp_name', 'constituency', 'allocated_amount_inr']
    
    # 2. Read MP (3) - Rajya Sabha & Nominated MPs
    df_mp3 = pd.read_csv('Dataset/Allocated Limit for Honble MPs (3).csv', header=None)
    df_mp3_clean = df_mp3.iloc[2:].copy()
    df_mp3_clean.columns = ['sr_no', 'state_ut', 'mp_name', 'house_type', 'allocated_amount_inr']
    df_mp3_clean['constituency'] = df_mp3_clean['state_ut'] + " (State At Large)"

    # Combine all MPs
    mp_list = []
    mp_idx = 1
    
    for _, r in df_mp2_clean.iterrows():
        st = str(r['state_ut']).strip() if not pd.isna(r['state_ut']) else "Maharashtra"
        name = str(r['mp_name']).strip() if not pd.isna(r['mp_name']) else "Hon'ble MP"
        const = str(r['constituency']).strip() if not pd.isna(r['constituency']) else "Constituency"
        try:
            amt = float(str(r['allocated_amount_inr']).replace(',', '').strip())
        except:
            amt = 147000000.0
            
        mp_list.append({
            "mp_id": f"MP_{mp_idx:03d}",
            "mp_name": name,
            "state_ut": st,
            "constituency": const,
            "district": const.split('_')[0].title(),
            "house_type": "Lok Sabha",
            "allocated_amount_inr": amt,
            "allocation_year": "2024-2025",
            "data_source": "Official Ministry Dataset (MP 2)"
        })
        mp_idx += 1

    for _, r in df_mp3_clean.iterrows():
        st = str(r['state_ut']).strip() if not pd.isna(r['state_ut']) else "Delhi"
        name = str(r['mp_name']).strip() if not pd.isna(r['mp_name']) else "Hon'ble MP"
        house = str(r['house_type']).strip() if not pd.isna(r['house_type']) else "Rajya Sabha"
        try:
            amt = float(str(r['allocated_amount_inr']).replace(',', '').strip())
        except:
            amt = 147000000.0
            
        mp_list.append({
            "mp_id": f"MP_{mp_idx:03d}",
            "mp_name": name,
            "state_ut": st,
            "constituency": f"{st} (Rajya Sabha)",
            "district": f"{st} Central",
            "house_type": house,
            "allocated_amount_inr": amt,
            "allocation_year": "2024-2025",
            "data_source": "Official Ministry Dataset (MP 3)"
        })
        mp_idx += 1

    df_mp_master = pd.DataFrame(mp_list)
    df_mp_master.to_csv('Dataset/mp_master.csv', index=False)
    print(f"Generated mp_master.csv with {len(df_mp_master)} official MPs.")

    # 3. Generate Implementing Agencies across States
    agency_types = [
        "Public Works Department (PWD)",
        "Municipal Infrastructure Corporation",
        "District Rural Development Agency (DRDA)",
        "State Water Supply & Sanitation Board",
        "Central Public Works Department (CPWD)",
        "National Buildings Construction Corporation (NBCC)"
    ]
    
    states = df_mp_master['state_ut'].unique()
    agency_list = []
    ag_id = 1
    
    for st in states:
        for a_type in agency_types:
            ag_name = f"{st} {a_type}"
            agency_list.append({
                "entity_id": f"AGENCY_{ag_id:03d}",
                "entity_name": ag_name,
                "state_ut": st,
                "district": f"{st} HQ",
                "entity_type": "Implementing Agency",
                "risk_score": float(np.random.choice([22.5, 35.0, 48.0, 65.0, 82.0], p=[0.2, 0.3, 0.3, 0.15, 0.05]))
            })
            ag_id += 1
            
    df_entities = pd.DataFrame(agency_list)
    df_entities.to_csv('Dataset/entities_corrected.csv', index=False)
    df_entities.to_csv('Dataset/entities.csv', index=False)
    print(f"Generated entities.csv with {len(df_entities)} state implementing agencies.")

    # 4. State Capitals Coordinates for Realistic Mapping
    STATE_COORDS = {
        'Maharashtra': (19.0760, 72.8777),
        'Tamil Nadu': (13.0827, 80.2707),
        'Uttar Pradesh': (26.8467, 80.9462),
        'West Bengal': (22.5726, 88.3639),
        'Bihar': (25.5941, 85.1376),
        'Karnataka': (12.9716, 77.5946),
        'Gujarat': (23.0225, 72.5714),
        'Rajasthan': (26.9124, 75.7873),
        'Kerala': (8.5241, 76.9366),
        'Punjab': (30.7333, 76.7794),
        'Haryana': (29.0588, 76.0856),
        'Delhi': (28.6139, 77.2090),
        'Madhya Pradesh': (23.2599, 77.4126),
        'Andhra Pradesh': (16.5062, 80.6480),
        'Telangana': (17.3850, 78.4867),
        'Odisha': (20.2961, 85.8245),
        'Assam': (26.1445, 91.7362),
        'Jammu And Kashmir': (34.0837, 74.7973),
        'Jharkhand': (23.3441, 85.3096),
        'Chhattisgarh': (21.2514, 81.6296),
        'Uttarakhand': (30.3165, 78.0322),
        'Himachal Pradesh': (31.1048, 77.1734),
        'Goa': (15.4989, 73.8278)
    }

    # 5. Generate Infrastructure Projects (~8 works per MP)
    categories = [
        "WATER_SUPPLY", "SCHOOL_INFRASTRUCTURE", "HEALTHCARE", 
        "ROAD_CONSTRUCTION", "SANITATION", "SOLAR_ENERGY", 
        "COMMUNITY_HALL", "DRAINAGE", "PUBLIC_TOILET", "BUS_SHELTER"
    ]
    
    desc_templates = {
        "WATER_SUPPLY": ["Installation of RO Drinking Water Plant", "Construction of Overhead Water Tank and Pipeline", "Deep Borewell Drilling & Submersible Pump Supply"],
        "SCHOOL_INFRASTRUCTURE": ["Construction of Additional Classrooms & Science Lab", "Digital Smart Classroom Setup & Computer Lab Supply", "School Library Building & Solar Electrification"],
        "HEALTHCARE": ["Upgradation of Maternity Ward & ICU Equipment", "Primary Health Centre Construction & Ambulance Supply", "Digital X-Ray & Diagnostic Equipment Procurement"],
        "ROAD_CONSTRUCTION": ["Bituminous Pavement Road Construction", "Concrete Village Connecting Road & Drainage Culvert", "Inter-Village Link Road Repair & Resurfacing"],
        "SANITATION": ["Community Toilet Complex Construction", "Underground RCC Sewage Line Network", "Solid Waste Processing & Sanitation Plant"],
        "SOLAR_ENERGY": ["Installation of Solar High-Mast Streetlights", "Solar Micro-Grid Setup for Village Power Supply", "Rooftop Solar Panel Installation on Civic Building"],
        "COMMUNITY_HALL": ["Construction of Multipurpose Community Hall", "Auditorium Building & Public Address System", "Village Panchayat Meeting Centre Building"],
        "DRAINAGE": ["Storm Water Drain Construction", "Concrete Covered Line Drain System", "Flood Control & Watershed Channel Works"],
        "PUBLIC_TOILET": ["Public Sanitation Complex Unit", "Highway Public Toilet Block", "Market Place Clean Sanitation Unit"],
        "BUS_SHELTER": ["Passenger Bus Waiting Shelter", "Modern Stainless Steel Bus Canopy", "Village Bus Stand & Commuter Amenities"]
    }

    anomalies = [
        "NORMAL", "NORMAL", "NORMAL", "NORMAL", "NORMAL", "NORMAL",
        "COST_OVERRUN", "PROJECT_DELAY", "DUPLICATE_PAYMENT_PATTERN",
        "FUND_UTILIZATION_ANOMALY", "FINANCIAL_PHYSICAL_MISMATCH",
        "UNUSUAL_TRANSACTION_PATTERN", "ABNORMAL_COMPLETION_RATE",
        "ENTITY_COMPLIANCE_ISSUE", "GEOGRAPHIC_INCONSISTENCY"
    ]

    proj_list = []
    trans_list = []
    proj_idx = 1
    trans_idx = 1
    
    base_date = datetime.date(2023, 4, 1)

    for _, mp in df_mp_master.iterrows():
        mp_id = mp['mp_id']
        mp_name = mp['mp_name']
        state_ut = mp['state_ut']
        constituency = mp['constituency']
        
        # Determine capital coordinates
        cap_lat, cap_lon = STATE_COORDS.get(state_ut, (20.5937, 78.9629))
        
        # Filter agencies in this state
        st_agencies = df_entities[df_entities['state_ut'] == state_ut]
        if st_agencies.empty:
            st_agencies = df_entities

        # Generate 8 projects per MP
        for k in range(8):
            p_id = f"PRJ{proj_idx:06d}"
            cat = random.choice(categories)
            desc = random.choice(desc_templates[cat]) + f" at {constituency} Locality #{k+1}"
            
            sanc_cost = round(random.uniform(500000.0, 5000000.0), -4)
            est_cost = sanc_cost
            
            scenario = random.choice(anomalies)
            status = random.choice(["Ongoing", "Ongoing", "Completed", "Sanctioned"])
            
            # Dates
            start_d = base_date + datetime.timedelta(days=random.randint(0, 300))
            sanc_d = start_d + datetime.timedelta(days=random.randint(10, 40))
            exp_comp_d = sanc_d + datetime.timedelta(days=random.randint(180, 360))
            act_comp_d = exp_comp_d + datetime.timedelta(days=random.randint(-30, 120)) if status == "Completed" else None
            
            # Progress & Expenditure based on Scenario
            if scenario == "NORMAL":
                phys_prog = 100.0 if status == "Completed" else random.uniform(25.0, 85.0)
                exp_val = sanc_cost if status == "Completed" else sanc_cost * (phys_prog / 100.0)
            elif scenario == "COST_OVERRUN":
                phys_prog = random.uniform(40.0, 75.0)
                exp_val = sanc_cost * random.uniform(1.25, 1.60) # Cost exceeds sanction!
            elif scenario == "PROJECT_DELAY":
                phys_prog = random.uniform(15.0, 40.0)
                exp_val = sanc_cost * 0.50
                exp_comp_d = base_date + datetime.timedelta(days=100) # Overdue!
            elif scenario == "FINANCIAL_PHYSICAL_MISMATCH":
                phys_prog = 5.0 # Physical progress stagnant
                exp_val = sanc_cost * 0.85 # Financial funds exhausted
            else:
                phys_prog = random.uniform(20.0, 80.0)
                exp_val = sanc_cost * (phys_prog / 100.0)

            lat = round(cap_lat + random.uniform(-0.45, 0.45), 6)
            lon = round(cap_lon + random.uniform(-0.45, 0.45), 6)
            
            agency_row = st_agencies.sample(1).iloc[0]
            agency_id = agency_row['entity_id']

            proj_list.append({
                "project_id": p_id,
                "work_description": desc,
                "work_category": cat,
                "mp_id": mp_id,
                "mp_name": mp_name,
                "constituency": constituency,
                "state_ut": state_ut,
                "district": mp['district'],
                "block_or_urban": f"Block-{k+1}",
                "village_or_locality": f"Locality-{k+1}",
                "estimated_cost_inr": est_cost,
                "sanctioned_cost_inr": sanc_cost,
                "start_date": start_d.strftime("%Y-%m-%d"),
                "sanction_date": sanc_d.strftime("%Y-%m-%d"),
                "expected_completion_date": exp_comp_d.strftime("%Y-%m-%d"),
                "actual_completion_date": act_comp_d.strftime("%Y-%m-%d") if act_comp_d else "",
                "status": status,
                "physical_completion_percentage": round(phys_prog, 1),
                "implementing_agency_id": agency_id,
                "latitude": lat,
                "longitude": lon,
                "anomaly_scenario": scenario
            })

            # Generate Fund Transactions for Project
            # 1. Sanction Transaction
            trans_list.append({
                "transaction_id": f"TRX{trans_idx:07d}",
                "project_id": p_id,
                "mp_id": mp_id,
                "transaction_type": "SANCTION",
                "amount_inr": sanc_cost,
                "transaction_date": sanc_d.strftime("%Y-%m-%d"),
                "payment_mode": "TREASURY_TRANSFER",
                "recipient_name": agency_row['entity_name']
            })
            trans_idx += 1

            # 2. Payment Disbursements
            if exp_val > 0:
                p_amt = exp_val / 2.0
                p_date1 = sanc_d + datetime.timedelta(days=30)
                trans_list.append({
                    "transaction_id": f"TRX{trans_idx:07d}",
                    "project_id": p_id,
                    "mp_id": mp_id,
                    "transaction_type": "EXPENDITURE",
                    "amount_inr": round(p_amt, 2),
                    "transaction_date": p_date1.strftime("%Y-%m-%d"),
                    "payment_mode": "PFMS_E_PAYMENT",
                    "recipient_name": agency_row['entity_name']
                })
                trans_idx += 1

                p_date2 = p_date1 + datetime.timedelta(days=45)
                trans_list.append({
                    "transaction_id": f"TRX{trans_idx:07d}",
                    "project_id": p_id,
                    "mp_id": mp_id,
                    "transaction_type": "EXPENDITURE",
                    "amount_inr": round(exp_val - p_amt, 2),
                    "transaction_date": p_date2.strftime("%Y-%m-%d"),
                    "payment_mode": "PFMS_E_PAYMENT",
                    "recipient_name": agency_row['entity_name']
                })
                trans_idx += 1

            proj_idx += 1

    df_projects = pd.DataFrame(proj_list)
    df_projects.to_csv('Dataset/projects_corrected.csv', index=False)
    df_projects.to_csv('Dataset/projects.csv', index=False)
    print(f"Generated projects_corrected.csv with {len(df_projects)} projects.")

    df_trans = pd.DataFrame(trans_list)
    df_trans.to_csv('Dataset/fund_transactions_corrected.csv', index=False)
    df_trans.to_csv('Dataset/fund_transactions.csv', index=False)
    print(f"Generated fund_transactions_corrected.csv with {len(df_trans)} financial transactions.")

    print("=== DATASET GENERATION SUCCESSFUL ===")

if __name__ == '__main__':
    generate_dataset()
