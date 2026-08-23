import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from sqlalchemy.orm import Session
from backend.app.models.models import Document, Work

def get_category_vendor_name(category: str, description: str) -> str:
    """Return realistic, category-matched vendor company name based on work category and description."""
    cat = (category or "").lower()
    desc = (description or "").lower()

    if "health" in cat or "hospital" in desc or "maternity" in desc or "icu" in desc or "clinic" in desc or "medical" in desc:
        return "MedTech Healthcare Infrastructure Ltd"
    elif "education" in cat or "computer" in desc or "lab" in desc or "school" in desc or "laptop" in desc:
        return "TechLine IT & Lab Equipment Solutions Pvt Ltd"
    elif "water" in cat or "drinking" in cat or "borewell" in desc or "pipe" in desc or "pump" in desc:
        return "AquaPure Water Systems & Drilling Corp"
    elif "road" in cat or "bridge" in cat or "pavement" in desc or "concreting" in desc or "culvert" in desc:
        return "Apex Infracon & Highway Contractors"
    elif "solar" in cat or "energy" in cat or "lighting" in desc or "power" in desc:
        return "SunPower Renewable Energy Systems"
    elif "sanitation" in cat or "drain" in desc or "toilet" in desc or "sewage" in desc:
        return "CleanWater Sanitation & Drainage Works"
    elif "community" in cat or "hall" in desc or "auditorium" in desc or "building" in desc:
        return "National Civic Infrastructure Developers"
    elif "irrigation" in cat or "dam" in desc or "canal" in desc:
        return "Jal Shakti Hydro Engineering Works"
    elif "sport" in cat or "gym" in desc or "playground" in desc:
        return "ProSport Infrastructure & Turf Solutions"
    elif "library" in cat or "reading" in desc or "digital" in desc:
        return "Knowledge Hub Publishers & IT Hardware"
    else:
        return "National Apex Infra Contractors"

def get_itemized_purchase_items(category: str, description: str, total_amount: float):
    """Generate realistic itemized goods, quantities, and unit costs matched to work category."""
    cat = (category or "").lower()
    desc = (description or "").lower()
    amt = max(100000.0, total_amount)

    if "health" in cat or "hospital" in desc or "maternity" in desc or "icu" in desc or "clinic" in desc or "medical" in desc:
        tot1 = amt * 0.45
        tot2 = amt * 0.30
        tot3 = amt * 0.15
        tot4 = amt * 0.10
        unit1_qty = max(2, int(tot1 / 225000))
        unit2_qty = max(5, int(tot2 / 45000))
        return [
            {"name": "Advanced Patient Monitor & Medical ICU Ventilator Units", "qty": f"{unit1_qty} units", "unit_cost": f"Rs. {tot1/unit1_qty:,.2f}", "total_cost": f"Rs. {tot1:,.2f}"},
            {"name": "Adjustable Electric Maternity Hospital Beds & Examination Tables", "qty": f"{unit2_qty} units", "unit_cost": f"Rs. {tot2/unit2_qty:,.2f}", "total_cost": f"Rs. {tot2:,.2f}"},
            {"name": "Portable Digital X-Ray & Ultrasound Diagnostic Medical Scanner", "qty": "1 unit", "unit_cost": f"Rs. {tot3:,.2f}", "total_cost": f"Rs. {tot3:,.2f}"},
            {"name": "Freight, Delivery, Logistics & Medical Equipment Sterilization Setup", "qty": "1 job", "unit_cost": f"Rs. {tot4:,.2f}", "total_cost": f"Rs. {tot4:,.2f}"}
        ]
    elif "education" in cat or "computer" in desc or "lab" in desc or "school" in desc or "laptop" in desc:
        unit1_qty = max(5, int((amt * 0.45) / 55000))
        unit1_cost = 55000.0
        tot1 = unit1_qty * unit1_cost

        unit2_qty = max(2, int((amt * 0.30) / 85000))
        unit2_cost = 85000.0
        tot2 = unit2_qty * unit2_cost

        unit3_qty = max(1, int((amt * 0.15) / 110000))
        unit3_cost = 110000.0
        tot3 = unit3_qty * unit3_cost

        tot4 = max(10000.0, amt - (tot1 + tot2 + tot3))

        return [
            {"name": "Dell OptiPlex 7090 Desktop Workstations (Intel i7, 16GB RAM, 512GB SSD)", "qty": f"{unit1_qty} units", "unit_cost": f"Rs. {unit1_cost:,.2f}", "total_cost": f"Rs. {tot1:,.2f}"},
            {"name": "Digital Laboratory Microscopes & Science Testing Kits", "qty": f"{unit2_qty} sets", "unit_cost": f"Rs. {unit2_cost:,.2f}", "total_cost": f"Rs. {tot2:,.2f}"},
            {"name": "Interactive Smart Classroom LED Display Boards (75-inch 4K)", "qty": f"{unit3_qty} units", "unit_cost": f"Rs. {unit3_cost:,.2f}", "total_cost": f"Rs. {tot3:,.2f}"},
            {"name": "Freight, Delivery, Logistics & On-Site Installation Charges", "qty": "1 job", "unit_cost": f"Rs. {tot4:,.2f}", "total_cost": f"Rs. {tot4:,.2f}"}
        ]
    elif "water" in cat or "drinking" in cat or "borewell" in desc or "pipe" in desc or "pump" in desc:
        tot1 = amt * 0.40
        tot2 = amt * 0.40
        tot3 = amt * 0.20
        return [
            {"name": "Submersible High-Capacity Water Pump Sets (15 HP 3-Phase)", "qty": "4 units", "unit_cost": f"Rs. {tot1/4:,.2f}", "total_cost": f"Rs. {tot1:,.2f}"},
            {"name": "Heavy Duty HDPE Pipeline Networks & Underground Connections (110mm)", "qty": "1,200 metres", "unit_cost": f"Rs. {tot2/1200:,.2f}/m", "total_cost": f"Rs. {tot2:,.2f}"},
            {"name": "Commercial RO Water Filtration & Chlorination Plant (2000 LPH)", "qty": "1 unit", "unit_cost": f"Rs. {tot3:,.2f}", "total_cost": f"Rs. {tot3:,.2f}"}
        ]
    elif "road" in cat or "bridge" in cat or "pavement" in desc or "concreting" in desc or "culvert" in desc:
        tot1 = amt * 0.50
        tot2 = amt * 0.35
        tot3 = amt * 0.15
        return [
            {"name": "Bituminous Concrete & Wearing Course Mixture (Grade-1 Quality)", "qty": "450 MT", "unit_cost": f"Rs. {tot1/450:,.2f}/MT", "total_cost": f"Rs. {tot1:,.2f}"},
            {"name": "Ready-Mix Reinforced Cement Concrete Mix (M30 Grade)", "qty": "180 cu.m", "unit_cost": f"Rs. {tot2/180:,.2f}/cu.m", "total_cost": f"Rs. {tot2:,.2f}"},
            {"name": "Heavy Machinery Compaction Roller & Excavator Usage Charges", "qty": "60 hours", "unit_cost": f"Rs. {tot3/60:,.2f}/hr", "total_cost": f"Rs. {tot3:,.2f}"}
        ]
    elif "solar" in cat or "energy" in cat or "lighting" in desc or "power" in desc:
        tot1 = amt * 0.45
        tot2 = amt * 0.35
        tot3 = amt * 0.20
        return [
            {"name": "High-Efficiency Monocrystalline Solar PV Panels (450W)", "qty": "80 units", "unit_cost": f"Rs. {tot1/80:,.2f}", "total_cost": f"Rs. {tot1:,.2f}"},
            {"name": "Solar Micro-Grid Inverters & Lithium Iron Battery Storage Units", "qty": "6 sets", "unit_cost": f"Rs. {tot2/6:,.2f}", "total_cost": f"Rs. {tot2:,.2f}"},
            {"name": "Outdoor High-Mast LED Solar Streetlight Galvanized Poles (12m)", "qty": "15 poles", "unit_cost": f"Rs. {tot3/15:,.2f}", "total_cost": f"Rs. {tot3:,.2f}"}
        ]
    elif "sanitation" in cat or "drain" in desc or "toilet" in desc or "sewage" in desc:
        tot1 = amt * 0.50
        tot2 = amt * 0.35
        tot3 = amt * 0.15
        return [
            {"name": "Modular Pre-fabricated Community Toilet Blocks & Sanitation Fixtures", "qty": "4 blocks", "unit_cost": f"Rs. {tot1/4:,.2f}", "total_cost": f"Rs. {tot1:,.2f}"},
            {"name": "Heavy Duty RCC Septic Tanks & Underground Drainage Pipe Networks (200mm)", "qty": "350 metres", "unit_cost": f"Rs. {tot2/350:,.2f}/m", "total_cost": f"Rs. {tot2:,.2f}"},
            {"name": "High-Pressure Sewage Suction Pump & Waste Treatment System", "qty": "1 unit", "unit_cost": f"Rs. {tot3:,.2f}", "total_cost": f"Rs. {tot3:,.2f}"}
        ]
    elif "community" in cat or "hall" in desc or "auditorium" in desc or "building" in desc:
        tot1 = amt * 0.50
        tot2 = amt * 0.30
        tot3 = amt * 0.20
        return [
            {"name": "Reinforced Cement Concrete Civil Structure & Brick Masonry Work", "qty": "1 lot", "unit_cost": f"Rs. {tot1:,.2f}", "total_cost": f"Rs. {tot1:,.2f}"},
            {"name": "Structural Steel Roof Trusses & Insulated Roofing Sheets", "qty": "350 sq.m", "unit_cost": f"Rs. {tot2/350:,.2f}/sq.m", "total_cost": f"Rs. {tot2:,.2f}"},
            {"name": "Acoustic Wall Panels & Public Address Audio System Setup", "qty": "1 set", "unit_cost": f"Rs. {tot3:,.2f}", "total_cost": f"Rs. {tot3:,.2f}"}
        ]
    else:
        tot1 = amt * 0.55
        tot2 = amt * 0.30
        tot3 = amt * 0.15
        return [
            {"name": "Infrastructure Works Material Procurement & Equipment Supply", "qty": "1 lot", "unit_cost": f"Rs. {tot1:,.2f}", "total_cost": f"Rs. {tot1:,.2f}"},
            {"name": "Physical Execution, Labour & Subcontractor Charges", "qty": "1 lot", "unit_cost": f"Rs. {tot2:,.2f}", "total_cost": f"Rs. {tot2:,.2f}"},
            {"name": "Quality Inspection, Engineering Supervision & Certification Fee", "qty": "1 job", "unit_cost": f"Rs. {tot3:,.2f}", "total_cost": f"Rs. {tot3:,.2f}"}
        ]

def generate_pdf_for_document(db: Session, doc: Document) -> str:
    """Generates an authentic, domain-matched PDF document file using ReportLab."""
    os.makedirs("documents", exist_ok=True)
    filename = f"{doc.document_type.replace(' ', '_')}_{doc.work_id or doc.id}.pdf"
    file_path = os.path.join("documents", filename).replace("\\", "/")

    if os.path.exists(file_path):
        return file_path

    work = db.query(Work).filter(Work.id == doc.work_id).first() if doc.work_id else None

    pdf = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    header_style = ParagraphStyle('HeaderStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=14, leading=18, alignment=1, textColor=colors.HexColor('#1e3a8a'))
    sub_header_style = ParagraphStyle('SubHeaderStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=14, alignment=1, textColor=colors.HexColor('#475569'))
    doc_title_style = ParagraphStyle('DocTitleStyle', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=13, leading=16, alignment=1, textColor=colors.HexColor('#0f172a'))
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=13, textColor=colors.HexColor('#334155'))
    bold_style = ParagraphStyle('BoldStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=colors.HexColor('#0f172a'))

    # Header section
    story.append(Paragraph("GOVERNMENT OF INDIA", header_style))
    story.append(Paragraph("MINISTRY OF STATISTICS AND PROGRAMME IMPLEMENTATION (MoSPI)", sub_header_style))
    story.append(Paragraph("MEMBER OF PARLIAMENT LOCAL AREA DEVELOPMENT SCHEME (MPLADS)", sub_header_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceAfter=10))

    # Document Title
    doc_type_name = doc.document_type.upper() if doc.document_type else "PURCHASE INVOICE & VENDOR BILL VOUCHER"
    story.append(Paragraph(f"OFFICIAL {doc_type_name}", doc_title_style))
    story.append(Spacer(1, 8))

    # Metadata Grid
    work_id_val = work.id if work else (doc.work_id or "N/A")
    amt_num = work.sanctioned_amount if work else 2500000.0
    sanction_amt = f"Rs. {amt_num:,.2f}"
    agency_name = work.implementing_agency.name if (work and work.implementing_agency) else (doc.extracted_data.get('agency') or "District Public Works Dept")
    mp_name = work.mp_name if work else "Hon'ble Member of Parliament"
    constituency = work.constituency if work else "District Constituency"
    sanction_date = work.sanction_date.strftime("%Y-%m-%d") if (work and work.sanction_date) else "2026-01-15"
    desc_text = work.description if work else "Supply of computers, laboratory equipment, and infrastructure works."
    vendor_name = (doc.extracted_data.get('vendor') if doc.extracted_data else None) or get_category_vendor_name(work.category if work else "", desc_text)

    meta_data = [
        [Paragraph("<b>Document Ref / Invoice No:</b>", body_style), Paragraph(f"INV-2026/{doc.id:05d}", bold_style), Paragraph("<b>Issue Date:</b>", body_style), Paragraph(sanction_date, bold_style)],
        [Paragraph("<b>Project ID:</b>", body_style), Paragraph(work_id_val, bold_style), Paragraph("<b>Status:</b>", body_style), Paragraph(work.status if work else "Sanctioned", bold_style)],
        [Paragraph("<b>Vendor / Contractor:</b>", body_style), Paragraph(f"<b>{vendor_name}</b>", bold_style), Paragraph("<b>Executing Agency:</b>", body_style), Paragraph(agency_name, body_style)],
        [Paragraph("<b>Recommending MP:</b>", body_style), Paragraph(f"{mp_name} ({constituency})", body_style), Paragraph("<b>GSTIN Registration:</b>", body_style), Paragraph(f"27AABCT{doc.id:04d}F1Z5", body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[130, 140, 120, 150])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Project Scope Description
    desc_text = work.description if work else "Supply of computers, laboratory equipment, and infrastructure works."
    story.append(Paragraph("<b>Project Scope & Purpose:</b>", bold_style))
    story.append(Paragraph(desc_text, body_style))
    story.append(Spacer(1, 10))

    # Itemized Purchased Goods & Costs Breakdown Table
    items = get_itemized_purchase_items(work.category if work else "Education", desc_text, amt_num)

    bill_data = [
        [Paragraph("<b>S.No</b>", bold_style), Paragraph("<b>Purchased Item Description & Model Specifications</b>", bold_style), Paragraph("<b>Qty</b>", bold_style), Paragraph("<b>Unit Rate</b>", bold_style), Paragraph("<b>Total Price</b>", bold_style)]
    ]
    for idx, itm in enumerate(items, 1):
        bill_data.append([
            Paragraph(f"{idx}.", body_style),
            Paragraph(itm["name"], body_style),
            Paragraph(itm["qty"], body_style),
            Paragraph(itm["unit_cost"], body_style),
            Paragraph(itm["total_cost"], body_style)
        ])
    
    bill_data.append([
        Paragraph("", bold_style),
        Paragraph("<b>TOTAL PURCHASE INVOICE ALLOCATION</b>", bold_style),
        Paragraph("", bold_style),
        Paragraph("", bold_style),
        Paragraph(f"<b>{sanction_amt}</b>", bold_style)
    ])

    bill_table = Table(bill_data, colWidths=[30, 240, 70, 95, 105])
    bill_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#94a3b8')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(bill_table)
    story.append(Spacer(1, 12))

    # AI Verification Badge Box
    is_verified = doc.consistency_score >= 90
    bg_color = colors.HexColor('#f0fdf4') if is_verified else colors.HexColor('#fff5f5')
    border_color = colors.HexColor('#16a34a') if is_verified else colors.HexColor('#dc2626')
    status_text = "✅ 100% VERIFIED — ALL PURCHASED ITEMS & COSTS MATCH SYSTEM DATABASE RECORDS" if is_verified else f"⚠️ DISCREPANCY ALERT ({doc.consistency_score:.0f}%) — ITEM COST / AGENCY MISMATCH DETECTED"

    verification_data = [
        [Paragraph(f"<b>MPLADS Sentinel AI Verification Audit:</b>", bold_style)],
        [Paragraph(status_text, ParagraphStyle('VStatus', parent=body_style, textColor=border_color, fontName='Helvetica-Bold'))]
    ]
    verification_table = Table(verification_data, colWidths=[540])
    verification_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_color),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(verification_table)
    story.append(Spacer(1, 16))

    # Page 1: Delivery Receipt & Signatures
    safe_vendor_name = str(vendor_name or "TechLine IT & Lab Equipment Solutions")
    sig_data = [
        [Paragraph("<b>Vendor Authorised Signatory:</b><br/>" + safe_vendor_name + "<br/><i>[Official Vendor Seal & Signature]</i>", body_style),
         Paragraph("<b>Physical Delivery Verification:</b><br/>MPLADS Inspection Officer<br/><i>[Goods Received & Stamped]</i>", body_style)]
    ]
    sig_table = Table(sig_data, colWidths=[270, 270])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(sig_table)

    # ----------------------------------------------------
    # PAGE 2: STATUTORY UTILIZATION CERTIFICATE (FORM GFR 12-C) & BANK UTR PROOF
    # ----------------------------------------------------
    from reportlab.platypus import PageBreak
    story.append(PageBreak())

    # Form GFR Header
    story.append(Paragraph("FORM GFR 12 - C", header_style))
    story.append(Paragraph("[See Rule 239]", sub_header_style))
    story.append(Paragraph("FORM OF UTILIZATION CERTIFICATE FOR AUTONOMOUS BODIES / EXECUTING AGENCIES", sub_header_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceAfter=10))

    story.append(Paragraph("<b>STATUTORY FUND UTILIZATION & AUDIT CERTIFICATE</b>", doc_title_style))
    story.append(Spacer(1, 8))

    uc_statement = f"""
    Certified that out of <b>{sanction_amt}</b> (Rupees) of Grants-in-Aid sanctioned during the financial period 2024-2026 under the Member of Parliament Local Area Development Scheme (MPLADS) in favour of <b>{agency_name}</b> for <i>"{desc_text}"</i> vide Ministry Sanction Order No. <b>MOSPI/MPLADS/{doc.id:05d}/2026</b> dated <b>{sanction_date}</b>, a sum of <b>{sanction_amt}</b> has been <b>100% FULLY UTILIZED</b> on buying actual specified items, civil materials, and equipment as per audited bank payment vouchers below.
    """
    story.append(Paragraph(uc_statement, body_style))
    story.append(Spacer(1, 10))

    # Bank Disbursal & Item Payment Voucher Proof Table
    story.append(Paragraph("<b>ITEMIZED BANK DISBURSAL VOUCHERS & UTR TRANSACTION PROOF:</b>", bold_style))
    story.append(Spacer(1, 4))

    tot1 = amt_num * 0.50
    tot2 = amt_num * 0.35
    tot3 = amt_num * 0.15

    vouchers_data = [
        [Paragraph("<b>Voucher No</b>", bold_style), Paragraph("<b>Payment Date</b>", bold_style), Paragraph("<b>Bank UTR Ref Number</b>", bold_style), Paragraph("<b>Beneficiary Vendor / Contractor</b>", bold_style), Paragraph("<b>Amount Paid (Rs.)</b>", bold_style), Paragraph("<b>Status</b>", bold_style)],
        [Paragraph("VCH-2026/01", body_style), Paragraph("12-Jan-2026", body_style), Paragraph("SBIN202601127819", body_style), Paragraph(safe_vendor_name, body_style), Paragraph(f"Rs. {tot1:,.2f}", body_style), Paragraph("SUCCESS ✅", bold_style)],
        [Paragraph("VCH-2026/02", body_style), Paragraph("28-Jan-2026", body_style), Paragraph("SBIN202601289104", body_style), Paragraph("Apex Cement & Raw Material Corp", body_style), Paragraph(f"Rs. {tot2:,.2f}", body_style), Paragraph("SUCCESS ✅", bold_style)],
        [Paragraph("VCH-2026/03", body_style), Paragraph("10-Feb-2026", body_style), Paragraph("SBIN202602104529", body_style), Paragraph("EarthMovers Equipment & Logistics", body_style), Paragraph(f"Rs. {tot3:,.2f}", body_style), Paragraph("SUCCESS ✅", bold_style)],
        [Paragraph("", bold_style), Paragraph("", bold_style), Paragraph("<b>TOTAL UTILIZED PROOF</b>", bold_style), Paragraph("", bold_style), Paragraph(f"<b>{sanction_amt}</b>", bold_style), Paragraph("<b>100% PAID</b>", bold_style)]
    ]

    vouchers_table = Table(vouchers_data, colWidths=[65, 65, 110, 150, 95, 55])
    vouchers_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#94a3b8')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ALIGN', (4,0), (4,-1), 'RIGHT'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(vouchers_table)
    story.append(Spacer(1, 14))

    # Audit Compliance Statement & Official Stamps
    audit_note = """
    <b>Financial Auditor Certification:</b><br/>
    We have verified the original purchase bills, bank payment receipts, debit vouchers, and stock entry registers maintained at the site office. The expenditure incurred matches the physical progress of work and goods delivered. No funds remain unspent or diverted.
    """
    story.append(Paragraph(audit_note, body_style))
    story.append(Spacer(1, 16))

    uc_sig_data = [
        [Paragraph("<b>Chartered Accountant / Finance Audit:</b><br/>M/s Sharma & Associates (ICAO Reg #048291)<br/><i>[Official Audit Seal & Signature]</i>", body_style),
         Paragraph("<b>District Collector & Nodal Authority:</b><br/>District Magistrate & Collectorate<br/><i>[Countersigned & Government Seal]</i>", body_style)]
    ]
    uc_sig_table = Table(uc_sig_data, colWidths=[270, 270])
    uc_sig_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(uc_sig_table)

    pdf.build(story)

    doc.file_path = file_path
    db.commit()

    return file_path
