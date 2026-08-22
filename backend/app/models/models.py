from sqlalchemy import Column, String, Integer, Float, Date, DateTime, Boolean, ForeignKey, Text, JSON, Table
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    
    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    state = Column(String(50), nullable=True)
    district = Column(String(50), nullable=True)
    constituency = Column(String(100), nullable=True)
    
    role = relationship("Role", back_populates="users")
    investigations = relationship("Investigation", back_populates="assigned_officer")

class State(Base):
    __tablename__ = 'states'
    code = Column(String(10), primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    districts = relationship("District", back_populates="state")
    works = relationship("Work", back_populates="state")

class District(Base):
    __tablename__ = 'districts'
    code = Column(String(10), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    state_code = Column(String(10), ForeignKey('states.code'), nullable=False)

    state = relationship("State", back_populates="districts")
    agencies = relationship("Agency", back_populates="district")
    works = relationship("Work", back_populates="district")

class Agency(Base):
    __tablename__ = 'agencies'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    district_code = Column(String(10), ForeignKey('districts.code'), nullable=True)
    completion_rate = Column(Float, default=0.0)
    average_delay_days = Column(Float, default=0.0)
    average_cost_deviation = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)

    district = relationship("District", back_populates="agencies")
    works = relationship("Work", back_populates="implementing_agency")

class Work(Base):
    __tablename__ = 'works'
    id = Column(String(50), primary_key=True, index=True)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    work_type = Column(String(100), nullable=True)
    mp_name = Column(String(100), nullable=False)
    constituency = Column(String(100), nullable=False)
    state_code = Column(String(10), ForeignKey('states.code'), nullable=True)
    district_code = Column(String(10), ForeignKey('districts.code'), nullable=True)
    block = Column(String(100), nullable=True)
    village = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    recommendation_date = Column(Date, nullable=True)
    sanction_date = Column(Date, nullable=True)
    expected_completion_date = Column(Date, nullable=True)
    actual_completion_date = Column(Date, nullable=True)
    status = Column(String(50), nullable=False, default="Sanctioned")
    implementing_agency_id = Column(Integer, ForeignKey('agencies.id'), nullable=True)
    estimated_cost = Column(Float, nullable=False)
    sanctioned_amount = Column(Float, nullable=False)
    expenditure = Column(Float, default=0.0)
    physical_progress = Column(Float, default=0.0)
    financial_progress = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    state = relationship("State", back_populates="works")
    district = relationship("District", back_populates="works")
    implementing_agency = relationship("Agency", back_populates="works")
    payments = relationship("Payment", back_populates="work")
    documents = relationship("Document", back_populates="work")
    investigations = relationship("Investigation", back_populates="work")
    alerts = relationship("Alert", back_populates="work")
    risk_scores = relationship("RiskScore", uselist=False, back_populates="work")

class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True, index=True)
    work_id = Column(String(50), ForeignKey('works.id'), nullable=False)
    payment_date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    payment_type = Column(String(50), nullable=True) # Milestone, Advance, Final
    transaction_ref = Column(String(100), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    work = relationship("Work", back_populates="payments")

class Rule(Base):
    __tablename__ = 'rules'
    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False) # CRITICAL, HIGH, MEDIUM, LOW
    condition_expression = Column(Text, nullable=False)
    threshold = Column(Float, nullable=False)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class RiskScore(Base):
    __tablename__ = 'risk_scores'
    work_id = Column(String(50), ForeignKey('works.id'), primary_key=True)
    overall_score = Column(Float, nullable=False, default=0.0)
    financial_risk = Column(Float, nullable=False, default=0.0)
    delay_risk = Column(Float, nullable=False, default=0.0)
    cost_risk = Column(Float, nullable=False, default=0.0)
    duplicate_risk = Column(Float, nullable=False, default=0.0)
    payment_risk = Column(Float, nullable=False, default=0.0)
    compliance_risk = Column(Float, nullable=False, default=0.0)
    document_risk = Column(Float, nullable=False, default=0.0)
    geographic_risk = Column(Float, nullable=False, default=0.0)
    factors = Column(JSON, nullable=False, default=list) # List of explanations
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    work = relationship("Work", back_populates="risk_scores")

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True, index=True)
    work_id = Column(String(50), ForeignKey('works.id'), nullable=True)
    document_type = Column(String(100), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    ocr_text = Column(Text, nullable=True)
    extracted_data = Column(JSON, nullable=True, default=dict)
    consistency_score = Column(Float, nullable=True)
    upload_date = Column(DateTime, default=datetime.utcnow)

    work = relationship("Work", back_populates="documents")

class Investigation(Base):
    __tablename__ = 'investigations'
    id = Column(Integer, primary_key=True, index=True)
    work_id = Column(String(50), ForeignKey('works.id'), nullable=False)
    assigned_to = Column(Integer, ForeignKey('users.id'), nullable=True)
    priority = Column(String(20), nullable=False) # CRITICAL, HIGH, MEDIUM, LOW
    status = Column(String(50), nullable=False, default="Detected") # Detected, Under Review, Assigned, Evidence Requested, Resolved
    findings = Column(Text, nullable=True)
    action_taken = Column(Text, nullable=True)
    resolution_state = Column(String(50), nullable=True) # False Positive, Corrective Action Required, Escalated, Verified Normal, Investigation Ongoing
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    work = relationship("Work", back_populates="investigations")
    assigned_officer = relationship("User", back_populates="investigations")
    actions = relationship("InvestigationAction", back_populates="investigation")

class InvestigationAction(Base):
    __tablename__ = 'investigation_actions'
    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey('investigations.id'), nullable=False)
    performed_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    action = Column(String(100), nullable=False) # Status Update, Add Findings, Assign
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    investigation = relationship("Investigation", back_populates="actions")

class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True, index=True)
    work_id = Column(String(50), ForeignKey('works.id'), nullable=False)
    alert_type = Column(String(50), nullable=False) # DUP_WORK, COST_OVERRUN, etc.
    severity = Column(String(20), nullable=False)
    score = Column(Float, nullable=False)
    reason = Column(Text, nullable=False)
    evidence = Column(JSON, nullable=True, default=dict)
    status = Column(String(20), nullable=False, default="ACTIVE") # ACTIVE, ACKNOWLEDGED, RESOLVED
    created_at = Column(DateTime, default=datetime.utcnow)

    work = relationship("Work", back_populates="alerts")

class SystemSetting(Base):
    __tablename__ = 'system_settings'
    key = Column(String(50), primary_key=True)
    value = Column(JSON, nullable=False)
