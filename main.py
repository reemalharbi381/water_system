import psycopg2
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from pydantic import BaseModel
import uuid
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_KEY = os.environ.get("GROQ_API_KEY", "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")
client = Groq(api_key=GROQ_KEY)
DB_URL = "postgresql://postgres:jCeYkVrnaQHuumtGZqsqmdbJlPvuZseZ@postgres.railway.internal:5432/railway"

# قاموس لترجمة رسائل النظام الثابتة
MESSAGES = {
    "ar": {
        "welcome": "نظام قطرة لإدارة المياه يعمل بنجاح",
        "service_success": "تم تسجيل طلب الزيارة الميدانية بنجاح",
        "replace_success": "تم استبدال العداد بنجاح. الرقم الجديد: ",
        "replace_denied": "العداد لا يحتاج استبدال حالياً.",
        "error": "حدث خطأ في النظام",
        "bot_fail": "أعتذر منك، أنا قطرة، حاول مرة أخرى لا هنت."
    },
    "en": {
        "welcome": "Qatrah Water Management System is running",
        "service_success": "Field service request registered successfully",
        "replace_success": "Meter replaced successfully. New Serial: ",
        "replace_denied": "Meter does not need replacement at this time.",
        "error": "System error occurred",
        "bot_fail": "I apologize, I am Qatrah, please try again."
    }
}

class FieldServiceRequest(BaseModel):
    customer_id: int
    account_id: int
    service_type: str
    description: str

@app.get("/")
async def home(lang: str = "ar"):
    return {"status": "success", "message": MESSAGES.get(lang, MESSAGES["ar"])["welcome"]}

@app.get("/chatbot")
async def chatbot(user_input: str, c_id: int = None, lang: str = "ar"):
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
                if lang == "ar":
                    context = f"العميل يملك {len(rows)} حسابات: " + ", ".join([f"حساب {r[0]} وعداد {r[1]}" for r in rows])
                else:
                    context = f"Customer has {len(rows)} accounts: " + ", ".join([f"Acc {r[0]} and meter is {r[1]}" for r in rows])
            cur.close()
            conn.close()
        except:
            context = ""

    system_prompt = f"Your name is Qatrah. {context}. Answer in {'Arabic' if lang == 'ar' else 'English'} language."
    if lang == "ar":
        system_prompt += " أجب بلهجة سعودية ودودة."

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )
        return {"reply": completion.choices[0].message.content}
    except:
        return {"reply": MESSAGES.get(lang, MESSAGES["ar"])["bot_fail"]}

@app.post("/field-service/request")
async def create_service_request(request: FieldServiceRequest, lang: str = "ar"):
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        query = """
            INSERT INTO field_services (customer_id, account_id, service_type, description, status) 
            VALUES (%s, %s, %s, %s, 'Pending')
        """
        cur.execute(query, (request.customer_id, request.account_id, request.service_type, request.description))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "message": MESSAGES.get(lang, MESSAGES["ar"])["service_success"]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/meter/replace/{account_id}")
async def replace_meter(account_id: int, lang: str = "ar"):
    texts = MESSAGES.get(lang, MESSAGES["ar"])
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT status, id FROM meters WHERE account_id = %s", (account_id,))
        result = cur.fetchone()

        if result and result[0] in ['تالف', 'مشكلة', 'damaged', 'faulty']:
            new_serial = f"MTR-{uuid.uuid4().hex[:6].upper()}"
            cur.execute("UPDATE meters SET meter_serial = %s, status = 'نشط' WHERE account_id = %s", (new_serial, account_id))
            conn.commit()
            return {"status": "success", "message": f"{texts['replace_success']}{new_serial}"}
        
        return {"status": "denied", "message": texts["replace_denied"]}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()