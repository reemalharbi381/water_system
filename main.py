import psycopg2
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from pydantic import BaseModel
from typing import Optional
import uuid
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None
DB_URL = "postgresql://postgres:jCeYkVrnaQHuumtGZqsqmdbJlPvuZseZ@postgres.railway.internal:5432/railway"

MESSAGES = {
    "ar": {
        "welcome": "نظام قطرة لإدارة المياه يعمل بنجاح",
        "service_success": "تم استلام طلبك وفتح تذكرة صيانة ميدانية بنجاح",
        "replace_success": "تم استبدال العداد بنجاح. الرقم الجديد: ",
        "bot_fail": "أعتذر منك، أنا قطرة، حاول مرة أخرى لا هنت."
    }
}

class UserAuth(BaseModel):
    username: str
    password: str

class ReadingRequest(BaseModel):
    meter_id: int
    reading_value: float

class ServiceAssignment(BaseModel):
    service_id: int
    technician_id: int

class FieldServiceRequest(BaseModel):
    customer_id: int
    account_id: int
    service_type: str
    description: str

def calculate_water_bill(consumption_m3: float):
    total_water_cost = 0
    remaining = consumption_m3
    s1 = min(remaining, 15)
    total_water_cost += s1 * 0.10
    remaining -= s1
    if remaining > 0:
        s2 = min(remaining, 15)
        total_water_cost += s2 * 1.00
        remaining -= s2
    if remaining > 0:
        s3 = min(remaining, 15)
        total_water_cost += s3 * 3.00
        remaining -= s3
    if remaining > 0:
        total_water_cost += remaining * 4.00
    total_bill = total_water_cost * 1.5
    return round(total_bill, 2)

@app.get("/")
async def home():
    return {"status": "success", "message": MESSAGES["ar"]["welcome"]}

@app.post("/login")
async def login(user: UserAuth):
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT id, role FROM users WHERE username = %s AND password_hash = %s", (user.username, user.password))
        found = cur.fetchone()
        cur.close()
        conn.close()
        if found: return {"status": "success", "user_id": found[0], "role": found[1]}
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        return {"error": str(e)}

@app.get("/chatbot")
async def chatbot(user_input: str, c_id: int = None):
    kb_answer = None
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT answer FROM chatbot_knowledge WHERE question ILIKE %s", (f'%{user_input}%',))
        res = cur.fetchone()
        if res: kb_answer = res[0]
        cur.close()
        conn.close()
    except: pass
    if kb_answer: return {"reply": kb_answer}
    if not client: return {"reply": MESSAGES["ar"]["bot_fail"]}
    prompt = f"اسمك 'قطرة'. أجب بلهجة سعودية ودودة. السياق: كود العميل {c_id}"
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": user_input}]
        )
        return {"reply": completion.choices[0].message.content}
    except:
        return {"reply": MESSAGES["ar"]["bot_fail"]}

@app.post("/meters/reading")
async def add_meter_reading(data: ReadingRequest):
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("INSERT INTO meter_readings (meter_id, reading_value) VALUES (%s, %s)", (data.meter_id, data.reading_value))
        cur.execute("SELECT account_id FROM meters WHERE id = %s", (data.meter_id,))
        acc_id = cur.fetchone()[0]
        bill_amount = calculate_water_bill(data.reading_value)
        cur.execute("""
            INSERT INTO invoices (account_id, amount_due, consumption_m3, due_date, status) 
            VALUES (%s, %s, %s, CURRENT_DATE + 15, 'Unpaid')
        """, (acc_id, bill_amount, data.reading_value))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "amount": bill_amount}
    except Exception as e:
        return {"error": str(e)}

@app.post("/field-service/request")
async def create_service_request(request: FieldServiceRequest):
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO service_requests (customer_id, meter_id, title, description, priority, status) 
            VALUES (%s, (SELECT id FROM meters WHERE account_id = %s LIMIT 1), %s, %s, 'Medium', 'Open')
            RETURNING id
        """, (request.customer_id, request.account_id, request.service_type, request.description))
        request_id = cur.fetchone()[0]
        cur.execute("""
            INSERT INTO field_services (customer_id, account_id, service_type, description, status) 
            VALUES (%s, %s, %s, %s, 'Pending Assignment')
        """, (request.customer_id, request.account_id, request.service_type, request.description))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "message": MESSAGES["ar"]["service_success"], "request_id": request_id}
    except Exception as e:
        return {"error": str(e)}

@app.get("/technicians/list")
async def list_technicians():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT id, full_name, specialty FROM technicians")
        techs = cur.fetchall()
        cur.close()
        conn.close()
        return [{"id": t[0], "name": t[1], "specialty": t[2]} for t in techs]
    except Exception as e:
        return {"error": str(e)}

@app.post("/services/assign")
async def assign_tech(data: ServiceAssignment):
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("UPDATE field_services SET technician_id = %s, status = 'In Progress' WHERE id = %s", 
                    (data.technician_id, data.service_id))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "message": "تم تعيين التقني بنجاح"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/customer/{c_id}/full-data")
async def get_all_data(c_id: int):
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("""
            SELECT a.account_number, m.meter_serial, i.amount_due, i.status
            FROM accounts a
            LEFT JOIN meters m ON a.id = m.account_id
            LEFT JOIN invoices i ON a.id = i.account_id
            WHERE a.customer_id = %s
        """, (c_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [{"acc": r[0], "meter": r[1], "bill": float(r[2]) if r[2] else 0, "status": r[3]} for r in rows]
    except Exception as e:
        return {"error": str(e)}

@app.post("/meter/replace/{account_id}")
async def replace_meter(account_id: int):
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        new_serial = f"MTR-{uuid.uuid4().hex[:6].upper()}"
        cur.execute("UPDATE meters SET meter_serial = %s, status = 'نشط' WHERE account_id = %s", (new_serial, account_id))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "message": f"{MESSAGES['ar']['replace_success']}{new_serial}"}
    except Exception as e:
        return {"error": str(e)}
    #1