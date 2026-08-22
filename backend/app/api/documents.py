from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.models import Document, Work, User, Alert
from backend.app.api.auth import get_current_user
from backend.app.schemas.schemas import DocumentResponse
from backend.app.ocr.extractor import extract_text_from_pdf, parse_extracted_entities, cross_validate_document
from backend.app.services.risk import update_all_risk_scores
import os
import shutil

router = APIRouter(prefix="/documents", tags=["Documents & OCR"])

UPLOAD_DIR = "documents"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    work_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Security: validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Save file to upload directory
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # Process Document: Extract text & entities
    raw_text = extract_text_from_pdf(file_path)
    extracted_data = parse_extracted_entities(raw_text, db)
    
    # Associate Work ID
    associated_work_id = work_id
    if not associated_work_id and extracted_data.get("work_id"):
        associated_work_id = extracted_data["work_id"]

    # Verify associated work exists
    if associated_work_id:
        work_exists = db.query(Work).filter(Work.id == associated_work_id).first()
        if not work_exists:
            # If the extracted work ID doesn't exist, we can clear it or log it
            associated_work_id = None

    # Create Document record
    doc = Document(
        work_id=associated_work_id,
        document_type=document_type,
        file_name=file.filename,
        file_path=file_path.replace("\\", "/"),
        ocr_text=raw_text,
        extracted_data=extracted_data,
        consistency_score=100.0 # Default
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Perform cross validation
    if associated_work_id:
        score, validations = cross_validate_document(db, doc)
        doc.consistency_score = score
        db.commit()

        # If consistency score is low (< 90%), trigger alert
        if score < 90.0:
            mismatches = [f"{v['field']} mismatch (Database: {v['db_val']} vs Document: {v['extracted_val']})" for v in validations if v["status"] == "MISMATCH"]
            reason_text = f"Document-Database cross validation checks failed with a consistency score of {score:.1f}%.\nMismatches: " + "; ".join(mismatches)
            
            existing_alert = db.query(Alert).filter(
                Alert.work_id == associated_work_id,
                Alert.alert_type == "RULE_DOC_MISMATCH",
                Alert.status == "ACTIVE"
            ).first()

            if not existing_alert:
                alert = Alert(
                    work_id=associated_work_id,
                    alert_type="RULE_DOC_MISMATCH",
                    severity="HIGH",
                    score=100.0 - score,
                    reason=reason_text,
                    evidence={"validations": validations, "document_id": doc.id}
                )
                db.add(alert)
                db.commit()

        # Update risk scores for this project
        update_all_risk_scores(db)

    return doc

@router.post("/{id}/process", response_model=DocumentResponse)
def reprocess_document(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="Physical document file missing on disk")

    raw_text = extract_text_from_pdf(doc.file_path)
    extracted_data = parse_extracted_entities(raw_text, db)
    
    doc.ocr_text = raw_text
    doc.extracted_data = extracted_data
    db.commit()

    if doc.work_id:
        score, validations = cross_validate_document(db, doc)
        doc.consistency_score = score
        db.commit()
        update_all_risk_scores(db)

    return doc

@router.get("/{id}/extractions")
def get_document_extractions(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    score, validations = cross_validate_document(db, doc)
    return {
        "document_id": doc.id,
        "work_id": doc.work_id,
        "consistency_score": score,
        "validations": validations,
        "extracted_data": doc.extracted_data
    }


