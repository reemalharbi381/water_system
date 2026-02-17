# ==================== BASIC SETUP ====================
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from datetime import datetime, date, timedelta
from typing import List, Optional, Any, Dict

import psycopg2
import psycopg2.extras
import torch
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# NOTE:
# الأفضل تحط DB_URL في Environment Variables بدل ما يكون مكتوب هنا.
DB_URL = os.getenv(
    "DB_URL",
    "postgresql://postgres:jCeYkVrnaQHuumtGZqsqmdbJlPvuZseZ@centerbeam.proxy.rlwy.net:24838/railway"
)

# ==================== APP ====================
app = FastAPI(title="Water System API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== DATABASE HELPERS ====================
def get_db_connection():
    return psycopg2.connect(DB_URL)

def fetch_all(sql: str, params: tuple = ()) -> list:
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def fetch_one(sql: str, params: tuple = ()) -> Optional[tuple]:
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql, params)
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()

def execute(sql: str, params: tuple = (), returning: bool = False) -> Optional[tuple]:
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql, params)
        row = cur.fetchone() if returning else None
        conn.commit()
        return row
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

# ==================== Pydantic Schemas ====================
class CustomerCreate(BaseModel):
    full_name: str
    phone_number: Optional[str] = None
    email: Optional[str] = None

class CustomerUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None

class SupportAnswer(BaseModel):
    pending_id: int
    answer: str

class ServiceRequestCreate(BaseModel):
    customer_id: int
    meter_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "normal"   # low/normal/high
    created_by: Optional[int] = None

class MaintenanceReportCreate(BaseModel):
    issue_type: str
    description: Optional[str] = None
    location: str
    urgency_level: Optional[str] = "normal"  # low/normal/high

class NewMeterRequestCreate(BaseModel):
    property_type: str
    owner_name: Optional[str] = None
    location: str
    contact_number: str

class MeterInspectionCreate(BaseModel):
    meter_number: str
    location: str
    contact_number: str
    additional_notes: Optional[str] = None

class FieldServiceCreate(BaseModel):
    customer_id: Optional[int] = None
    account_id: Optional[int] = None
    technician_id: Optional[int] = None
    service_type: Optional[str] = None
    scheduled_date: Optional[str] = None  # ISO string
    status: Optional[str] = "scheduled"

class MeterReadingCreate(BaseModel):
    meter_id: int
    reading_value: float
    reading_date: Optional[str] = None   # ISO: "2026-02-17T10:00:00" (اختياري)
    is_manual: Optional[bool] = True

# ==================== CHATBOT (Lazy Loading) ====================
# Lazy load to reduce memory / load time
MODEL = None
UTIL = None
KB_QUESTIONS: List[str] = []
KB_ANSWERS: List[str] = []
KB_EMBEDDINGS = None
KB_LOADED = False

RAG_THRESHOLD = float(os.getenv("RAG_THRESHOLD", "0.60"))  # ارفعها عشان ما يرد وهو مو فاهم

def ensure_chatbot_loaded():
    global MODEL, UTIL, KB_QUESTIONS, KB_ANSWERS, KB_EMBEDDINGS, KB_LOADED

    if KB_LOADED:
        return

    try:
        from sentence_transformers import SentenceTransformer, util
        UTIL = util
        # نموذج خفيف نسبيًا
        MODEL = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot model load failed: {str(e)}")

    rows = fetch_all("SELECT question, answer FROM chatbot_knowledge")
    if not rows:
        KB_QUESTIONS, KB_ANSWERS, KB_EMBEDDINGS = [], [], None
        KB_LOADED = True
        return

    KB_QUESTIONS = [r[0] for r in rows]
    KB_ANSWERS = [r[1] for r in rows]
    KB_EMBEDDINGS = MODEL.encode(KB_QUESTIONS, convert_to_tensor=True)

    KB_LOADED = True

def reload_chatbot_knowledge():
    global KB_LOADED
    KB_LOADED = False
    ensure_chatbot_loaded()

def save_pending_question(question: str):
    execute(
        """
        INSERT INTO pending_support (user_query, status)
        VALUES (%s, 'pending')
        """,
        (question,),
        returning=False
    )

# =========================
# CUSTOMERS CRUD
# =========================
@app.get("/customers")
def list_customers():
    rows = fetch_all("""
        SELECT id, full_name, phone_number, email
        FROM customers
        ORDER BY id DESC
    """)
    return [
        {"id": r[0], "full_name": r[1], "phone_number": r[2], "email": r[3]}
        for r in rows
    ]

@app.get("/customers/{customer_id}")
def get_customer(customer_id: int):
    r = fetch_one("""
        SELECT id, full_name, phone_number, email
        FROM customers
        WHERE id = %s
    """, (customer_id,))
    if not r:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"id": r[0], "full_name": r[1], "phone_number": r[2], "email": r[3]}

@app.post("/customers")
def create_customer(payload: CustomerCreate):
    try:
        row = execute("""
            INSERT INTO customers (full_name, phone_number, email)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (payload.full_name, payload.phone_number, payload.email), returning=True)
        new_id = row[0]
        return {"id": new_id, "full_name": payload.full_name, "phone_number": payload.phone_number, "email": payload.email}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/customers/{customer_id}")
def update_customer(customer_id: int, payload: CustomerUpdate):
    old = fetch_one("SELECT full_name, phone_number, email FROM customers WHERE id=%s", (customer_id,))
    if not old:
        raise HTTPException(status_code=404, detail="Customer not found")

    full_name = payload.full_name if payload.full_name is not None else old[0]
    phone_number = payload.phone_number if payload.phone_number is not None else old[1]
    email = payload.email if payload.email is not None else old[2]

    try:
        execute("""
            UPDATE customers
            SET full_name=%s, phone_number=%s, email=%s
            WHERE id=%s
        """, (full_name, phone_number, email, customer_id))
        return {"id": customer_id, "full_name": full_name, "phone_number": phone_number, "email": email}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int):
    try:
        row = execute("DELETE FROM customers WHERE id=%s RETURNING id", (customer_id,), returning=True)
        if not row:
            raise HTTPException(status_code=404, detail="Customer not found")
        return {"status": "success", "deleted_id": customer_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== CHATBOT (RAG) ====================
@app.get("/chatbot")
def chatbot(inquiry: str = Query(..., min_length=1)):
    inquiry = inquiry.strip()
    if not inquiry:
        raise HTTPException(status_code=400, detail="السؤال فارغ")

    ensure_chatbot_loaded()

    if KB_EMBEDDINGS is None:
        save_pending_question(inquiry)
        return {"reply": "لم أتمكن من إيجاد إجابة، تم تحويل سؤالك لموظف خدمة العملاء.", "mode": "Human_Handoff"}

    user_vec = MODEL.encode(inquiry, convert_to_tensor=True)
    scores = UTIL.cos_sim(user_vec, KB_EMBEDDINGS)[0]

    best_score = float(torch.max(scores))
    best_index = int(torch.argmax(scores))

    if best_score >= RAG_THRESHOLD:
        return {
            "reply": KB_ANSWERS[best_index],
            "confidence": round(best_score, 3),
            "mode": "RAG"
        }

    save_pending_question(inquiry)
    return {"reply": "سؤالك يحتاج تدخل بشري، تم تحويله لموظف خدمة العملاء.", "mode": "Human_Handoff"}

# ==================== SUPPORT (HUMAN) ====================
@app.get("/support/pending")
def get_pending_support():
    rows = fetch_all("""
        SELECT id, user_query, status, created_at
        FROM pending_support
        WHERE status = 'pending'
        ORDER BY created_at ASC
    """)
    return [{"id": r[0], "question": r[1], "status": r[2], "created_at": r[3]} for r in rows]

@app.post("/support/answer")
def answer_pending_question(data: SupportAnswer):
    row = fetch_one("SELECT user_query FROM pending_support WHERE id=%s", (data.pending_id,))
    if not row:
        raise HTTPException(status_code=404, detail="السؤال غير موجود")

    question = row[0]
    try:
        execute("""
            INSERT INTO chatbot_knowledge (question, answer)
            VALUES (%s, %s)
        """, (question, data.answer))

        execute("""
            UPDATE pending_support
            SET status='answered'
            WHERE id=%s
        """, (data.pending_id,))

        reload_chatbot_knowledge()

        return {"status": "success", "saved_question": question, "saved_answer": data.answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== PORTAL (CUSTOMER VIEW) ====================
@app.get("/portal/summary")
def portal_summary(customer_id: int = Query(...)):
    # accounts count
    accounts_count = fetch_one("SELECT COUNT(*) FROM accounts WHERE customer_id=%s", (customer_id,))[0]
    meters_count = fetch_one("""
        SELECT COUNT(*)
        FROM meters m
        JOIN accounts a ON a.id = m.account_id
        WHERE a.customer_id=%s
    """, (customer_id,))[0]
    unpaid_invoices = fetch_one("""
        SELECT COUNT(*)
        FROM invoices i
        JOIN accounts a ON a.id = i.account_id
        WHERE a.customer_id=%s AND (i.status ILIKE 'unpaid' OR i.status='Unpaid')
    """, (customer_id,))[0]
    open_requests = fetch_one("""
        SELECT COUNT(*)
        FROM service_requests
        WHERE customer_id=%s AND COALESCE(status,'') NOT ILIKE 'completed'
    """, (customer_id,))[0]

    return {
        "customer_id": customer_id,
        "accounts_count": accounts_count,
        "meters_count": meters_count,
        "unpaid_invoices": unpaid_invoices,
        "open_requests": open_requests,
    }

@app.get("/portal/accounts")
def portal_list_accounts(customer_id: int = Query(...)):
    rows = fetch_all("""
        SELECT id, customer_id, account_number, address, account_type
        FROM accounts
        WHERE customer_id=%s
        ORDER BY id DESC
    """, (customer_id,))
    return [
        {
            "id": r[0],
            "customer_id": r[1],
            "account_number": r[2],
            "address": r[3],
            "account_type": r[4],
        } for r in rows
    ]

@app.get("/portal/meters")
def portal_list_meters(customer_id: int = Query(...)):
    rows = fetch_all("""
        SELECT m.id, m.account_id, m.serial_number, m.installation_date, m.status
        FROM meters m
        JOIN accounts a ON a.id = m.account_id
        WHERE a.customer_id=%s
        ORDER BY m.id DESC
    """, (customer_id,))
    return [
        {
            "id": r[0],
            "account_id": r[1],
            "serial_number": r[2],
            "installation_date": str(r[3]) if r[3] else None,
            "status": r[4],
        } for r in rows
    ]

@app.get("/portal/invoices")
def portal_list_invoices(customer_id: int = Query(...), status: Optional[str] = Query(None)):
    sql = """
        SELECT i.id, i.account_id, i.consumption_m3, i.amount_due, i.issue_date, i.due_date, i.status
        FROM invoices i
        JOIN accounts a ON a.id = i.account_id
        WHERE a.customer_id=%s
    """
    params = [customer_id]
    if status:
        sql += " AND i.status ILIKE %s"
        params.append(status)
    sql += " ORDER BY i.issue_date DESC NULLS LAST, i.id DESC"

    rows = fetch_all(sql, tuple(params))
    return [
        {
            "id": r[0],
            "account_id": r[1],
            "consumption_m3": float(r[2]) if r[2] is not None else None,
            "amount_due": float(r[3]) if r[3] is not None else None,
            "issue_date": str(r[4]) if r[4] else None,
            "due_date": str(r[5]) if r[5] else None,
            "status": r[6],
        } for r in rows
    ]

@app.get("/portal/meter-readings")
def portal_list_meter_readings(meter_id: int = Query(...)):
    rows = fetch_all("""
        SELECT id, meter_id, reading_value, reading_date, is_manual
        FROM meter_readings
        WHERE meter_id=%s
        ORDER BY reading_date DESC NULLS LAST, id DESC
        LIMIT 50
    """, (meter_id,))
    return [
        {
            "id": r[0],
            "meter_id": r[1],
            "reading_value": float(r[2]),
            "reading_date": r[3].isoformat() if r[3] else None,
            "is_manual": r[4],
        } for r in rows
    ]

@app.post("/portal/meter-readings")
def portal_add_meter_reading(payload: MeterReadingCreate):
    # تأكد العداد موجود + account_id
    meter = fetch_one("SELECT id, account_id FROM meters WHERE id=%s", (payload.meter_id,))
    if not meter:
        raise HTTPException(status_code=404, detail="Meter not found")

    account_id = meter[1]
    if not account_id:
        raise HTTPException(status_code=400, detail="meter غير مربوط بـ account_id")

    # آخر قراءة سابقة (عشان نحسب الاستهلاك)
    prev = fetch_one("""
        SELECT reading_value
        FROM meter_readings
        WHERE meter_id=%s
        ORDER BY reading_date DESC NULLS LAST, id DESC
        LIMIT 1
    """, (payload.meter_id,))
    prev_value = float(prev[0]) if prev else 0.0

    if float(payload.reading_value) < prev_value:
        raise HTTPException(status_code=400, detail=f"New reading أقل من السابقة ({prev_value})")

    # Parse reading_date (اختياري) أو استخدم NOW() تلقائي
    rd_dt = None
    if payload.reading_date:
        try:
            rd_dt = datetime.fromisoformat(payload.reading_date)
        except Exception:
            raise HTTPException(status_code=400, detail="reading_date must be ISO format e.g. 2026-02-17T10:00:00")

    # INSERT reading + رجّع reading_value + reading_date
    try:
        new_row = execute("""
            INSERT INTO meter_readings (meter_id, reading_value, reading_date, is_manual)
            VALUES (%s, %s, COALESCE(%s, NOW()), %s)
            RETURNING id, reading_value, reading_date
        """, (
            payload.meter_id,
            payload.reading_value,
            rd_dt,  # None -> NOW()
            payload.is_manual if payload.is_manual is not None else True
        ), returning=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    new_reading_id = int(new_row[0])
    new_reading_value = float(new_row[1])
    new_reading_date = new_row[2]  # datetime

    consumption = round(new_reading_value - prev_value, 3)

    # --------- AUTO BILLING (Residential slabs) ----------
    # جلب الشرائح (كلها residential حاليا)
    tiers = fetch_all("""
        SELECT min_consumption, max_consumption, price_per_m3, sewage_fee_percent
        FROM billing_tiers
        WHERE account_type='residential' OR account_type IS NULL
        ORDER BY min_consumption ASC
    """)

    if not tiers:
        raise HTTPException(status_code=400, detail="لا توجد شرائح في billing_tiers")

    water_cost = 0.0
    sewage_percent = None

    for (min_c, max_c, price, sewage_p) in tiers:
        if sewage_percent is None and sewage_p is not None:
            sewage_percent = float(sewage_p)

        min_c = float(min_c or 0.0)
        max_c = float(max_c or 999999999.0)
        price = float(price or 0.0)

        # كمية الشريحة = من min إلى max ضمن الاستهلاك
        slab_qty = max(0.0, min(consumption, max_c) - min_c)
        if slab_qty > 0:
            water_cost += slab_qty * price

    if sewage_percent is None:
        sewage_percent = 0.0

    sewage_cost = water_cost * (sewage_percent / 100.0)
    total_amount = round(water_cost + sewage_cost, 2)

    issue_date = date.today()
    due_date = issue_date + timedelta(days=30)

    try:
        invoice_id = execute("""
            INSERT INTO invoices (account_id, consumption_m3, amount_due, issue_date, due_date, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (account_id, consumption, total_amount, issue_date, due_date, "Unpaid"), returning=True)[0]
    except Exception as e:
        # لو فشل توليد الفاتورة، ما نخرب القراءة، لكن نوضح الخطأ
        raise HTTPException(status_code=500, detail=f"Reading saved لكن فشل إنشاء الفاتورة: {str(e)}")

    return {
        "status": "success",
        "meter_id": payload.meter_id,
        "reading_id": new_reading_id,
        "reading_date": new_reading_date.isoformat() if new_reading_date else None,
        "previous_reading": prev_value,
        "new_reading": new_reading_value,
        "consumption_m3": consumption,
        "invoice_id": int(invoice_id),
        "amount_due": total_amount,
        "issue_date": str(issue_date),
        "due_date": str(due_date),
        "invoice_status": "Unpaid",
        "sewage_fee_percent": sewage_percent,
    }

# ==================== CUSTOMER REQUESTS / COMPLAINTS ====================
@app.post("/portal/service-requests")
def portal_create_service_request(payload: ServiceRequestCreate):
    # request_code بسيط
    request_code = f"SR-{int(datetime.utcnow().timestamp())}"

    try:
        row = execute("""
            INSERT INTO service_requests (request_code, customer_id, meter_id, title, description, priority, status, created_by, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            RETURNING id
        """, (
            request_code,
            payload.customer_id,
            payload.meter_id,
            payload.title,
            payload.description,
            payload.priority,
            "new",
            payload.created_by
        ), returning=True)
        return {"status": "success", "request_id": int(row[0]), "request_code": request_code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portal/service-requests")
def portal_list_service_requests(customer_id: int = Query(...), status: Optional[str] = Query(None)):
    sql = """
        SELECT id, request_code, customer_id, meter_id, title, description, priority, status, created_at, updated_at
        FROM service_requests
        WHERE customer_id=%s
    """
    params = [customer_id]
    if status:
        sql += " AND status ILIKE %s"
        params.append(status)
    sql += " ORDER BY created_at DESC NULLS LAST, id DESC"

    rows = fetch_all(sql, tuple(params))
    return [
        {
            "id": r[0],
            "request_code": r[1],
            "customer_id": r[2],
            "meter_id": r[3],
            "title": r[4],
            "description": r[5],
            "priority": r[6],
            "status": r[7],
            "created_at": r[8].isoformat() if r[8] else None,
            "updated_at": r[9].isoformat() if r[9] else None,
        } for r in rows
    ]

# ==================== MAINTENANCE REPORTS ====================
@app.post("/portal/maintenance-reports")
def portal_create_maintenance_report(payload: MaintenanceReportCreate):
    try:
        row = execute("""
            INSERT INTO maintenance_reports (issue_type, description, location, urgency_level, status, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            RETURNING id
        """, (payload.issue_type, payload.description, payload.location, payload.urgency_level, "new"), returning=True)
        return {"status": "success", "report_id": int(row[0])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portal/maintenance-reports")
def portal_list_maintenance_reports(status: Optional[str] = Query(None)):
    sql = """
        SELECT id, issue_type, description, location, urgency_level, status, created_at
        FROM maintenance_reports
        WHERE 1=1
    """
    params = []
    if status:
        sql += " AND status ILIKE %s"
        params.append(status)
    sql += " ORDER BY created_at DESC NULLS LAST, id DESC"

    rows = fetch_all(sql, tuple(params))
    return [
        {
            "id": r[0],
            "issue_type": r[1],
            "description": r[2],
            "location": r[3],
            "urgency_level": r[4],
            "status": r[5],
            "created_at": r[6].isoformat() if r[6] else None,
        } for r in rows
    ]

# ==================== NEW METER REQUESTS ====================
@app.post("/portal/new-meter-requests")
def portal_create_new_meter_request(payload: NewMeterRequestCreate):
    try:
        row = execute("""
            INSERT INTO new_meter_requests (property_type, owner_name, location, contact_number, status, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            RETURNING id
        """, (payload.property_type, payload.owner_name, payload.location, payload.contact_number, "new"), returning=True)
        return {"status": "success", "request_id": int(row[0])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portal/new-meter-requests")
def portal_list_new_meter_requests(status: Optional[str] = Query(None)):
    sql = """
        SELECT id, property_type, owner_name, location, contact_number, status, created_at
        FROM new_meter_requests
        WHERE 1=1
    """
    params = []
    if status:
        sql += " AND status ILIKE %s"
        params.append(status)
    sql += " ORDER BY created_at DESC NULLS LAST, id DESC"

    rows = fetch_all(sql, tuple(params))
    return [
        {
            "id": r[0],
            "property_type": r[1],
            "owner_name": r[2],
            "location": r[3],
            "contact_number": r[4],
            "status": r[5],
            "created_at": r[6].isoformat() if r[6] else None,
        } for r in rows
    ]

# ==================== METER INSPECTIONS ====================
@app.post("/portal/meter-inspections")
def portal_create_meter_inspection(payload: MeterInspectionCreate):
    try:
        row = execute("""
            INSERT INTO meter_inspections (meter_number, location, contact_number, additional_notes, status, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            RETURNING id
        """, (payload.meter_number, payload.location, payload.contact_number, payload.additional_notes, "new"), returning=True)
        return {"status": "success", "inspection_id": int(row[0])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portal/meter-inspections")
def portal_list_meter_inspections(status: Optional[str] = Query(None)):
    sql = """
        SELECT id, meter_number, location, contact_number, additional_notes, status, created_at
        FROM meter_inspections
        WHERE 1=1
    """
    params = []
    if status:
        sql += " AND status ILIKE %s"
        params.append(status)
    sql += " ORDER BY created_at DESC NULLS LAST, id DESC"

    rows = fetch_all(sql, tuple(params))
    return [
        {
            "id": r[0],
            "meter_number": r[1],
            "location": r[2],
            "contact_number": r[3],
            "additional_notes": r[4],
            "status": r[5],
            "created_at": r[6].isoformat() if r[6] else None,
        } for r in rows
    ]

# ==================== FIELD SERVICES (VISITS) ====================
@app.post("/portal/field-services")
def portal_create_field_service(payload: FieldServiceCreate):
    sch_dt = None
    if payload.scheduled_date:
        try:
            sch_dt = datetime.fromisoformat(payload.scheduled_date)
        except Exception:
            raise HTTPException(status_code=400, detail="scheduled_date must be ISO e.g. 2026-02-17T10:00:00")

    try:
        row = execute("""
            INSERT INTO field_services (customer_id, account_id, technician_id, service_type, scheduled_date, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            payload.customer_id,
            payload.account_id,
            payload.technician_id,
            payload.service_type,
            sch_dt,
            payload.status or "scheduled"
        ), returning=True)
        return {"status": "success", "field_service_id": int(row[0])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portal/field-services")
def portal_list_field_services(customer_id: Optional[int] = Query(None), status: Optional[str] = Query(None)):
    sql = """
        SELECT id, customer_id, account_id, technician_id, service_type, scheduled_date, status
        FROM field_services
        WHERE 1=1
    """
    params = []
    if customer_id is not None:
        sql += " AND customer_id=%s"
        params.append(customer_id)
    if status:
        sql += " AND status ILIKE %s"
        params.append(status)

    sql += " ORDER BY scheduled_date DESC NULLS LAST, id DESC"

    rows = fetch_all(sql, tuple(params))
    return [
        {
            "id": r[0],
            "customer_id": r[1],
            "account_id": r[2],
            "technician_id": r[3],
            "service_type": r[4],
            "scheduled_date": r[5].isoformat() if r[5] else None,
            "status": r[6],
        } for r in rows
    ]

# ==================== HEALTH CHECK ====================
@app.get("/")
def health():
    return {"status": "Water System API is running"}