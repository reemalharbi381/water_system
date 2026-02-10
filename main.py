# ==================== BASIC SETUP ====================
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import torch
import psycopg2
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util


# ==================== APP ====================
app = FastAPI(title="Water System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== DATABASE ====================
DB_URL = "postgresql://postgres:jCeYkVrnaQHuumtGZqsqmdbJlPvuZseZ@centerbeam.proxy.rlwy.net:24838/railway"

def get_db_connection():
    return psycopg2.connect(DB_URL)


# ==================== MODELS ====================
class SupportAnswer(BaseModel):
    pending_id: int
    answer: str


# ==================== AI MODEL ====================
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

KB_QUESTIONS: List[str] = []
KB_ANSWERS: List[str] = []
KB_EMBEDDINGS = None


def load_chatbot_knowledge():
    global KB_QUESTIONS, KB_ANSWERS, KB_EMBEDDINGS

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT question, answer FROM chatbot_knowledge")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    if not rows:
        KB_QUESTIONS = []
        KB_ANSWERS = []
        KB_EMBEDDINGS = None
        return

    KB_QUESTIONS = [r[0] for r in rows]
    KB_ANSWERS = [r[1] for r in rows]
    KB_EMBEDDINGS = model.encode(KB_QUESTIONS, convert_to_tensor=True)


# تحميل المعرفة عند تشغيل السيرفر
load_chatbot_knowledge()


# ==================== HELPERS ====================
def save_pending_question(question: str):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO pending_support (user_query, status)
        VALUES (%s, 'pending')
        """,
        (question,)
    )

    conn.commit()
    cur.close()
    conn.close()


# ==================== CHATBOT (RAG) ====================
@app.get("/chatbot")
def chatbot(inquiry: str):
    inquiry = inquiry.strip()

    if not inquiry:
        raise HTTPException(status_code=400, detail="السؤال فارغ")

    # إذا ما فيه معرفة
    if KB_EMBEDDINGS is None:
        save_pending_question(inquiry)
        return {
            "reply": "لم أتمكن من إيجاد إجابة، تم تحويل سؤالك لموظف خدمة العملاء.",
            "mode": "Human_Handoff"
        }

    user_vec = model.encode(inquiry, convert_to_tensor=True)
    scores = util.cos_sim(user_vec, KB_EMBEDDINGS)[0]

    best_score = float(torch.max(scores))
    best_index = int(torch.argmax(scores))

    if best_score >= 0.45:
        return {
            "reply": KB_ANSWERS[best_index],
            "confidence": round(best_score, 3),
            "mode": "RAG"
        }

    # فشل → موظف بشري
    save_pending_question(inquiry)
    return {
        "reply": "سؤالك يحتاج تدخل بشري، تم تحويله لموظف خدمة العملاء.",
        "mode": "Human_Handoff"
    }


# ==================== SUPPORT (HUMAN) ====================
@app.get("/support/pending")
def get_pending_support():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, user_query, status, created_at
        FROM pending_support
        WHERE status = 'pending'
        ORDER BY created_at ASC
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "id": r[0],
            "question": r[1],
            "status": r[2],
            "created_at": r[3]
        }
        for r in rows
    ]


@app.post("/support/answer")
def answer_pending_question(data: SupportAnswer):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # جلب السؤال
        cur.execute(
            "SELECT user_query FROM pending_support WHERE id = %s",
            (data.pending_id,)
        )
        row = cur.fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="السؤال غير موجود")

        question = row[0]

        # حفظه في المعرفة
        cur.execute(
            """
            INSERT INTO chatbot_knowledge (question, answer)
            VALUES (%s, %s)
            """,
            (question, data.answer)
        )

        # تحديث الحالة
        cur.execute(
            """
            UPDATE pending_support
            SET status = 'answered'
            WHERE id = %s
            """,
            (data.pending_id,)
        )

        conn.commit()

        # تحديث المعرفة والـ embeddings فورًا
        load_chatbot_knowledge()

        return {
            "status": "success",
            "saved_question": question,
            "saved_answer": data.answer
        }

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cur.close()
        conn.close()


# ==================== HEALTH CHECK ====================
@app.get("/")
def health():
    return {"status": "Water System API is running"}