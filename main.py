from fastapi import FastAPI
import psycopg2
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


DB_URL = "postgresql://postgres:jCeYkVrnaQHuumtGZqsqmdbJlPvuZseZ@postgres.railway.internal:5432/railway"

def get_db_connection():
    return psycopg2.connect(DB_URL)

@app.get("/")
def home():
    return {"message": "Water System API is running!"}


@app.get("/chatbot")
def chatbot(query: str):
    conn = get_db_connection()
    cur = conn.cursor()
    search_sql = """
        SELECT answer_text FROM (
            SELECT answer_text FROM chatbot_knowledge WHERE question_key ILIKE %s
            UNION ALL
            SELECT staff_answer FROM customer_inquiries WHERE question_text ILIKE %s AND is_common = TRUE
        ) AS results LIMIT 1;
    """
    cur.execute(search_sql, (f'%{query}%', f'%{query}%'))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return {"reply": result[0] if result else "I will save your question for our staff!"}


@app.get("/customer/{c_id}/invoices")
def get_invoices(c_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT invoice_date, amount, status FROM invoices WHERE customer_id = %s", (c_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"date": r[0], "amount": r[1], "status": r[2]} for r in rows]
#final update check