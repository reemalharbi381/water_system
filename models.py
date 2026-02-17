from pydantic import BaseModel
from typing import Optional


# =========================
# ACCOUNTS
# =========================
class AccountBase(BaseModel):
    customer_id: Optional[int] = None
    account_number: str
    address: Optional[str] = None
    account_type: Optional[str] = None


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    customer_id: Optional[int] = None
    account_number: Optional[str] = None
    address: Optional[str] = None
    account_type: Optional[str] = None


class AccountOut(AccountBase):
    id: int


# =========================
# BILLING TIERS
# =========================
class BillingTierBase(BaseModel):
    tier_name: Optional[str] = None
    min_consumption: Optional[float] = None
    max_consumption: Optional[float] = None
    price_per_m3: Optional[float] = None
    sewage_fee_percent: Optional[float] = None


class BillingTierCreate(BillingTierBase):
    pass


class BillingTierUpdate(BillingTierBase):
    pass


class BillingTierOut(BillingTierBase):
    id: int


# =========================
# CHATBOT KNOWLEDGE
# =========================
class ChatbotKnowledgeBase(BaseModel):
    question: str
    answer: str


class ChatbotKnowledgeCreate(ChatbotKnowledgeBase):
    pass


class ChatbotKnowledgeUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None


class ChatbotKnowledgeOut(ChatbotKnowledgeBase):
    id: int


# =========================
# CUSTOMER INQUIRIES
# =========================
class CustomerInquiryBase(BaseModel):
    customer_id: Optional[int] = None
    question_text: Optional[str] = None
    staff_answer: Optional[str] = None
    is_common: Optional[bool] = None


class CustomerInquiryCreate(CustomerInquiryBase):
    pass


class CustomerInquiryUpdate(CustomerInquiryBase):
    pass


class CustomerInquiryOut(CustomerInquiryBase):
    id: int


# =========================
# CUSTOMERS
# =========================
class CustomerBase(BaseModel):
    full_name: str
    phone_number: Optional[str] = None
    email: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None


class CustomerOut(CustomerBase):
    id: int


# =========================
# FIELD SERVICE
# =========================
class FieldServiceBase(BaseModel):
    customer_id: Optional[int] = None
    account_id: Optional[int] = None
    technician_id: Optional[int] = None
    service_type: Optional[str] = None
    scheduled_date: Optional[str] = None
    status: Optional[str] = None


class FieldServiceCreate(FieldServiceBase):
    pass


class FieldServiceUpdate(FieldServiceBase):
    pass


class FieldServiceOut(FieldServiceBase):
    id: int


# =========================
# INVOICES
# =========================
class InvoiceBase(BaseModel):
    account_id: Optional[int] = None
    consumption_m3: Optional[float] = None
    amount_due: Optional[float] = None
    issue_date: Optional[str] = None
    due_date: Optional[str] = None
    status: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceUpdate(InvoiceBase):
    pass


class InvoiceOut(InvoiceBase):
    id: int


# =========================
# MAINTENANCE REPORTS
# =========================
class MaintenanceReportBase(BaseModel):
    issue_type: str
    description: Optional[str] = None
    location: str
    urgency_level: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None


class MaintenanceReportCreate(MaintenanceReportBase):
    pass


class MaintenanceReportUpdate(BaseModel):
    issue_type: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    urgency_level: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None


class MaintenanceReportOut(MaintenanceReportBase):
    id: int


# =========================
# METER INSPECTIONS
# =========================
class MeterInspectionBase(BaseModel):
    meter_number: str
    location: str
    contact_number: str
    additional_notes: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None


class MeterInspectionCreate(MeterInspectionBase):
    pass


class MeterInspectionUpdate(BaseModel):
    meter_number: Optional[str] = None
    location: Optional[str] = None
    contact_number: Optional[str] = None
    additional_notes: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None


class MeterInspectionOut(MeterInspectionBase):
    id: int


# =========================
# METERS
# =========================
class MeterBase(BaseModel):
    account_id: Optional[int] = None
    serial_number: str
    installation_date: Optional[str] = None
    status: Optional[str] = None


class MeterCreate(MeterBase):
    pass


class MeterUpdate(BaseModel):
    account_id: Optional[int] = None
    serial_number: Optional[str] = None
    installation_date: Optional[str] = None
    status: Optional[str] = None


class MeterOut(MeterBase):
    id: int


# =========================
# METER READINGS
# =========================
class MeterReadingBase(BaseModel):
    meter_id: Optional[int] = None
    reading_value: float
    reading_date: Optional[str] = None
    is_manual: Optional[bool] = None


class MeterReadingCreate(MeterReadingBase):
    pass


class MeterReadingUpdate(BaseModel):
    meter_id: Optional[int] = None
    reading_value: Optional[float] = None
    reading_date: Optional[str] = None
    is_manual: Optional[bool] = None


class MeterReadingOut(MeterReadingBase):
    id: int


# =========================
# NEW METER REQUESTS
# =========================
class NewMeterRequestBase(BaseModel):
    property_type: str
    owner_name: Optional[str] = None
    location: str
    contact_number: str
    status: Optional[str] = None
    created_at: Optional[str] = None


class NewMeterRequestCreate(NewMeterRequestBase):
    pass


class NewMeterRequestUpdate(BaseModel):
    property_type: Optional[str] = None
    owner_name: Optional[str] = None
    location: Optional[str] = None
    contact_number: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None


class NewMeterRequestOut(NewMeterRequestBase):
    id: int


# =========================
# PENDING SUPPORT
# =========================
class PendingSupportBase(BaseModel):
    user_query: str
    status: Optional[str] = None
    created_at: Optional[str] = None


class PendingSupportCreate(PendingSupportBase):
    pass


class PendingSupportUpdate(BaseModel):
    user_query: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None


class PendingSupportOut(PendingSupportBase):
    id: int


# =========================
# SERVICE REQUESTS
# =========================
class ServiceRequestBase(BaseModel):
    request_code: str
    customer_id: int
    meter_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ServiceRequestCreate(ServiceRequestBase):
    pass


class ServiceRequestUpdate(BaseModel):
    request_code: Optional[str] = None
    customer_id: Optional[int] = None
    meter_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ServiceRequestOut(ServiceRequestBase):
    id: int


# =========================
# TECHNICIANS
# =========================
class TechnicianBase(BaseModel):
    full_name: str
    specialty: Optional[str] = None
    phone_number: Optional[str] = None


class TechnicianCreate(TechnicianBase):
    pass


class TechnicianUpdate(BaseModel):
    full_name: Optional[str] = None
    specialty: Optional[str] = None
    phone_number: Optional[str] = None


class TechnicianOut(TechnicianBase):
    id: int


# =========================
# USERS
# =========================
class UserBase(BaseModel):
    username: str
    password_hash: str
    role: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password_hash: Optional[str] = None
    role: Optional[str] = None


class UserOut(UserBase):
    id: int

class PortalAccess(BaseModel):
    id: int
    customer_id: int
    access_code: str
    expires_at: str
    created_at: Optional[str]    