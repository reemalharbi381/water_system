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

API_KEYS = [
    "AIzaSyBqLY6mih3iIcx0BYCrqEwGDt4dwQgw_fk",
    "AIzaSyC-_etncXNX2Oxviy5YjEHU8soDTJ6mXQU",
    "AIzaSyCgjnyS5rj4v1XpYRWRs6NIf9F0amq48Ug"
]

DB_URL = "postgresql://postgres:jCeYkVrnaQHuumtGZqsqmdbJlPvuZseZ@postgres.railway.internal:5432/railway"

def get_db_connection():
    return psycopg2.connect(DB_URL)

@app.get("/")
async def home():
    return {
        "status": "success",
        "bot_name": "Qatrah / قطرة"
    }

@app.get("/chatbot")
async def chatbot(user_input: str):
    for key in API_KEYS:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            context = (
                "Your name is 'Qatrah' (قطرة). Assistant for Water Management System. "
                "Respond in the user's language (Arabic/English). Be concise."
            )
            
            response = model.generate_content(f"{context}\nUser: {user_input}")
            return {"reply": response.text}
            
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                continue 
            return {"reply": "Technical glitch.", "error": str(e)}
    
    return {"reply": "All lines busy, try later."}

@app.get("/customer/{c_id}/invoices")
async def get_invoices(c_id: int):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT invoice_date, amount, status FROM invoices WHERE customer_id = %s", (c_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [{"date": str(r[0]), "amount": float(r[1]), "status": r[2]} for r in rows]
    except Exception as e:
        return {"error": str(e)}