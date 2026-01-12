import google.generativeai as genai
import psycopg2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

genai.configure(api_key="AIzaSyCgjnyS5rj4v1XpYRWRs6NIf9F0amq48Ug")
model = genai.GenerativeModel('gemini-2.0-flash')

DB_URL = "postgresql://postgres:jCeYkVrnaQHuumtGZqsqmdbJlPvuZseZ@postgres.railway.internal:5432/railway"

def get_db_connection():
    return psycopg2.connect(DB_URL)

@app.get("/")
async def home():
    return {
        "status": "success",
        "bot_name": "Qatrah / قطرة",
        "welcome_note": "Welcome! I am Qatrah, your water assistant. How can I help you today? / أهلاً بك! أنا قطرة، مساعدك الذكي للمياه. كيف يمكنني مساعدتك اليوم؟"
    }

@app.get("/chatbot")
async def chatbot(user_input: str):
    context = (
        "Your name is 'Qatrah' (قطرة). You are a professional assistant for a Water Management System. "
        "Detect the user's language automatically. If the user speaks Arabic, respond in Arabic. "
        "If the user speaks English, respond in English. Always introduce yourself as Qatrah if asked. "
        "Keep your answers polite and helpful."
    )
    
    full_prompt = f"{context}\nUser question: {user_input}"
    
    response = model.generate_content(full_prompt)
    return {"reply": response.text}

@app.get("/customer/{c_id}/invoices")
async def get_invoices(c_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT invoice_date, amount, status FROM invoices WHERE customer_id = %s", (c_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"date": str(r[0]), "amount": float(r[1]), "status": r[2]} for r in rows]