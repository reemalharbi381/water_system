import google.generativeai as genai
import psycopg2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# AI Configuration (Using your API Key)
genai.configure(api_key="AIzaSyCgjnyS5rj4v1XpYRWRs6NIf9F0amq48Ug")
model = genai.GenerativeModel('gemini-2.0-flash')

# Database connection details
DB_URL = "postgresql://postgres:jCeYkVrnaQHuumtGZqsqmdbJlPvuZseZ@postgres.railway.internal:5432/railway"

def get_db_connection():
    return psycopg2.connect(DB_URL)

@app.get("/")
async def home():
    return {"message": "Water System API is running successfully"}

# NEW: AI Chatbot (Replaces the old SQL-based search)
@app.get("/chatbot")
async def chatbot(user_input: str):
    context = "You are a professional assistant for a Water Management System. Provide helpful and polite answers about water conservation and general inquiries in English."
    full_prompt = f"{context}\nUser question: {user_input}"
    
    response = model.generate_content(full_prompt)
    return {"reply": response.text}

# Keep the invoices function as it is needed for the dashboard
@app.get("/customer/{c_id}/invoices")
async def get_invoices(c_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT invoice_date, amount, status FROM invoices WHERE customer_id = %s", (c_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"date": str(r[0]), "amount": float(r[1]), "status": r[2]} for r in rows]
