from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# User Schemas
class UserBase(BaseModel):
    username: str
    role_id: int
    state: Optional[str] = None
    district: Optional[str] = None
    constituency: Optional[str] = None

class UserResponse(UserBase):
    id: int
    role_name: str

    class Config:
        from_attributes = True

# Login schema
class LoginRequest(BaseModel):
    username: str
    password: str

# Role Schema
class RoleResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

# State & District Schemas
class DistrictResponse(BaseModel):
    code: str
    name: str
    state_code: str

    class Config:
        from_attributes = True

class StateResponse(BaseModel):
    code: str
    name: str
    districts: List[DistrictResponse] = []

    class Config:
        from_attributes = True

# Agency Schemas
class AgencyBase(BaseModel):
    name: str
    district_code: Optional[str] = None

class AgencyResponse(AgencyBase):
    id: int
    completion_rate: float
    average_delay_days: float
    average_cost_deviation: float
    risk_score: float

    class Config:
        from_attributes = True

# Payment Schemas
class PaymentBase(BaseModel):
    work_id: str
    payment_date: date
    amount: float
    payment_type: Optional[str] = None
    transaction_ref: Optional[str] = None

class PaymentResponse(PaymentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# RiskScore Schema
class RiskScoreResponse(BaseModel):
    work_id: str
    overall_score: float
    financial_risk: float
    delay_risk: float
    cost_risk: float
    duplicate_risk: float
    payment_risk: float
    compliance_risk: float
    document_risk: float
    geographic_risk: float
    factors: List[str]
    updated_at: datetime

    class Config:
        from_attributes = True

# Work Schemas
class WorkBase(BaseModel):
    id: str
    description: str
    category: str
    work_type: Optional[str] = None
    mp_name: str
    constituency: str
    state_code: Optional[str] = None
    district_code: Optional[str] = None
    block: Optional[str] = None
    village: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    recommendation_date: Optional[date] = None
    sanction_date: Optional[date] = None
    expected_completion_date: Optional[date] = None
    actual_completion_date: Optional[date] = None
    status: str
    implementing_agency_id: Optional[int] = None
    estimated_cost: float
    sanctioned_amount: float
    expenditure: float
    physical_progress: float
    financial_progress: float

class WorkResponse(WorkBase):
    created_at: datetime
    implementing_agency_name: Optional[str] = None
    risk_scores: Optional[RiskScoreResponse] = None
    primary_attribution: Optional[str] = None
    backtrack_summary: Optional[str] = None

    class Config:
        from_attributes = True

# Rule Schemas
class RuleBase(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    category: str
    severity: str
    condition_expression: str
    threshold: float
    enabled: bool = True

class RuleResponse(RuleBase):
    created_at: datetime

    class Config:
        from_attributes = True

class RuleUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    condition_expression: Optional[str] = None
    threshold: Optional[float] = None
    enabled: Optional[bool] = None

# Alert Schemas
class AlertResponse(BaseModel):
    id: int
    work_id: str
    alert_type: str
    severity: str
    score: float
    reason: str
    evidence: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    work_description: Optional[str] = None

    class Config:
        from_attributes = True

class AlertStatusUpdate(BaseModel):
    status: str

# Document Schemas
class DocumentResponse(BaseModel):
    id: int
    work_id: Optional[str] = None
    document_type: str
    file_name: str
    file_path: str
    ocr_text: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    consistency_score: Optional[float] = None
    upload_date: datetime

    class Config:
        from_attributes = True

# Investigation Schemas
class InvestigationActionResponse(BaseModel):
    id: int
    investigation_id: int
    performed_by_name: str
    action: str
    notes: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class InvestigationResponse(BaseModel):
    id: int
    work_id: str
    work_description: Optional[str] = None
    assigned_to_name: Optional[str] = None
    assigned_to_id: Optional[int] = None
    priority: str
    status: str
    findings: Optional[str] = None
    action_taken: Optional[str] = None
    resolution_state: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    actions: List[InvestigationActionResponse] = []

    class Config:
        from_attributes = True

class InvestigationCreate(BaseModel):
    work_id: str
    priority: str = "MEDIUM"
    assigned_to: Optional[int] = None

class InvestigationUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[int] = None
    findings: Optional[str] = None
    action_taken: Optional[str] = None
    resolution_state: Optional[str] = None

# AI Assistant Schemas
class AIQueryRequest(BaseModel):
    query: str

class AIQueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, str]]
