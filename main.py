import psycopg2
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from pydantic import BaseModel
import uuid
import os

app = FastAPI()

# 1. إعدادات CORS للسماح لـ React بالاتصال بالـ API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# جلب مفتاح Groq من بيئة النظام (Railway) لضمان الأمان وتجاوز حظر GitHub
GROQ_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

# رابط قاعدة البيانات من Railway
DB_URL = "postgresql://postgres:jCeYkVrnaQHuumtGZqsqmdbJlPvuZseZ@postgres.railway.internal:5432/railway"

# رسائل النظام الموحدة
MESSAGES = {
    "ar": {
        "welcome": "نظام قطرة لإدارة المياه يعمل بنجاح",
        "service_success": "تم تسجيل طلب الزيارة الميدانية بنجاح",
        "replace_success": "تم استبدال العداد بنجاح. الرقم الجديد: ",
        "replace_denied": "العداد لا يحتاج استبدال حالياً.",
        "bot_fail": "أعتذر منك، أنا قطرة، حاول مرة أخرى لا هنت."
    },
    "en": {
        "welcome": "Qatrah Water Management System is running",
        "service_success": "Field service request registered successfully",
        "replace_success": "Meter replaced successfully. New Serial: ",
        "replace_denied": "Meter does not need replacement at this time.",
        "bot_fail": "I apologize, I am Qatrah, please try again."
    }
}

class FieldServiceRequest(BaseModel):
    customer_id: int
    account_id: int
    service_type: str
    description: str

# وظيفة حساب الفاتورة بناءً على نظام الشرائح السعودي
def calculate_water_bill(consumption_m3: float):
    total_water_cost = 0
    remaining = consumption_m3

    # الشريحة الأولى: حتى 15 م3 بسعر 0.10 ريال
    s1 = min(remaining, 15)
    total_water_cost += s1 * 0.10
    remaining -= s1

    # الشريحة الثانية: من 16 م3 إلى 30 م3 بسعر 1.00 ريال
    if remaining > 0:
        s2 = min(remaining, 15)
        total_water_cost += s2 * 1.00
        remaining -= s2

    # الشريحة الثالثة: من 31 م3 إلى 45 م3 بسعر 3.00 ريال
    if remaining > 0:
        s3 = min(remaining, 15)
        total_water_cost += s3 * 3.00
        remaining -= s3

    # الشريحة الرابعة: ما زاد عن 45 م3 بسعر 4.00 ريال
    if remaining > 0:
        total_water_cost += remaining * 4.00

    # رسوم الصرف الصحي: 50% من قيمة استهلاك المياه (كما ورد في الصورة)
    sanitation_cost = total_water_cost * 0.50
    
    total_bill = total_water_cost + sanitation_cost
    return round(total_bill, 2)

@app.get("/")
async def home(lang: str = "ar"):
    return {"status": "success", "message": MESSAGES.get(lang, MESSAGES["ar"])["welcome"]}

@app.get("/chatbot")
async def chatbot(user_input: str, c_id: int = None, lang: str = "ar"):
    if not client:
        return {"reply": "API Key is missing. Please set GROQ_API_KEY in Railway."}
    
    context = ""
    if c_id:
        try:
            conn = psycopg2.connect(DB_URL)
            cur = conn.cursor()
            cur.execute("""
                SELECT a.account_number, m.status 
                FROM accounts a 
                JOIN meters m ON a.id = m.account_id 
                WHERE a.customer_id = %s
            """, (c_id,))
            rows = cur.fetchall()
            if rows:
                context = f"العميل لديه {len(rows)} حسابات."
            cur.close()
            conn.close()
        except:
            context = ""

    system_prompt = f"اسمك 'قطرة'. أجب بلهجة سعودية ودودة ومهنية. لغة الرد: {'العربية' if lang == 'ar' else 'English'}. السياق: {context}"

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}]
        )
        return {"reply": completion.choices[0].message.content}
    except:
        return {"reply": MESSAGES.get(lang, MESSAGES["ar"])["bot_fail"]}

@app.post("/invoices/generate/{account_id}")
async def generate_bill(account_id: int, consumption: float):
    try:
        bill_amount = calculate_water_bill(consumption)
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        query = """
            INSERT INTO invoices (account_id, amount, consumption_m3, due_date, status) 
            VALUES (%s, %s, %s, CURRENT_DATE + INTERVAL '15 days', 'Unpaid')
            RETURNING id;
        """
        cur.execute(query, (account_id, bill_amount, consumption))
        invoice_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "invoice_id": invoice_id, "amount": bill_amount}
    except Exception as e:
        return {"error": str(e)}

@app.post("/field-service/request")
async def create_service_request(request: FieldServiceRequest, lang: str = "ar"):
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        query = "INSERT INTO field_services (customer_id, account_id, service_type, description) VALUES (%s, %s, %s, %s)"
        cur.execute(query, (request.customer_id, request.account_id, request.service_type, request.description))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "message": MESSAGES.get(lang, MESSAGES["ar"])["service_success"]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/meter/replace/{account_id}")
async def replace_meter(account_id: int, lang: str = "ar"):
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        new_serial = f"MTR-{uuid.uuid4().hex[:6].upper()}"
        cur.execute("UPDATE meters SET meter_serial = %s, status = 'نشط' WHERE account_id = %s", (new_serial, account_id))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "message": f"{MESSAGES.get(lang)['replace_success']}{new_serial}"}
    except Exception as e:
        return {"error": str(e)}