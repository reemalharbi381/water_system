import psycopg2
import requests
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

@app.get("/")
async def home():
    return {"status": "success", "bot_name": "Qatrah / قطرة"}

@app.get("/chatbot")
async def chatbot(user_input: str):
    for key in API_KEYS:
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={key}"
        payload = {
            "contents": [{
                "parts": [{"text": f"Your name is Qatrah (قطرة). Assistant for Water Management. Respond in user language. User: {user_input}"}]
            }]
        }
        try:
            response = requests.post(url, json=payload, timeout=15)
            data = response.json()
            if response.status_code == 200:
                return {"reply": data['candidates'][0]['content']['parts'][0]['text']}
            continue
        except:
            continue
    return {"reply": "عذراً، النظام يواجه ضغطاً حالياً، يرجى المحاولة مرة أخرى."}

@app.get("/customer/{c_id}/invoices")
async def get_invoices(c_id: int):
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT invoice_date, amount, status FROM invoices WHERE customer_id = %s", (c_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [{"date": str(r[0]), "amount": float(r[1]), "status": r[2]} for r in rows]
    except Exception as e:
        return {"error": str(e)}