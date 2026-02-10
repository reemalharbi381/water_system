from pydantic import BaseModel
from typing import Optional


class Account(BaseModel):
    id: int
    customer_id: Optional[int]
    account_number: str
    address: Optional[str]
    account_type: Optional[str]


class BillingTier(BaseModel):
    id: int
    tier_name: Optional[str]
    min_consumption: Optional[float]
    max_consumption: Optional[float]
    price_per_m3: Optional[float]
    sewage_fee_percent: Optional[float]


class ChatbotKnowledge(BaseModel):
    id: int
    question: str
    answer: str


class CustomerInquiry(BaseModel):
    id: int
    customer_id: Optional[int]
    question_text: Optional[str]
    staff_answer: Optional[str]
    is_common: Optional[bool]


class Customer(BaseModel):
    id: int
    full_name: str
    phone_number: Optional[str]
    email: Optional[str]


class FieldService(BaseModel):
    id: int
    customer_id: Optional[int]
    account_id: Optional[int]
    technician_id: Optional[int]
    service_type: Optional[str]
    scheduled_date: Optional[str]
    status: Optional[str]


class Invoice(BaseModel):
    id: int
    account_id: Optional[int]
    consumption_m3: Optional[float]
    amount_due: Optional[float]
    issue_date: Optional[str]
    due_date: Optional[str]
    status: Optional[str]


class MaintenanceReport(BaseModel):
    id: int
    issue_type: str
    description: Optional[str]
    location: str
    urgency_level: Optional[str]
    status: Optional[str]
    created_at: Optional[str]


class MeterInspection(BaseModel):
    id: int
    meter_number: str
    location: str
    contact_number: str
    additional_notes: Optional[str]
    status: Optional[str]
    created_at: Optional[str]


class MeterReading(BaseModel):
    id: int
    meter_id: Optional[int]
    reading_value: float
    reading_date: Optional[str]
    is_manual: Optional[bool]


class Meter(BaseModel):
    id: int
    account_id: Optional[int]
    serial_number: str
    installation_date: Optional[str]
    status: Optional[str]


class NewMeterRequest(BaseModel):
    id: int
    property_type: str
    owner_name: Optional[str]
    location: str
    contact_number: str
    status: Optional[str]
    created_at: Optional[str]


class PendingSupport(BaseModel):
    id: int
    user_query: str
    status: Optional[str]
    created_at: Optional[str]


class ServiceRequest(BaseModel):
    id: int
    request_code: str
    customer_id: int
    meter_id: Optional[int]
    title: str
    description: Optional[str]
    priority: Optional[str]
    status: Optional[str]
    created_by: Optional[int]
    created_at: Optional[str]
    updated_at: Optional[str]


class Technician(BaseModel):
    id: int
    full_name: str
    specialty: Optional[str]
    phone_number: Optional[str]


class User(BaseModel):
    id: int
    username: str
    password_hash: str
    role: Optional[str]