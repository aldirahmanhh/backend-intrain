
import json
import uuid
import re
import random as rd

from core.db import db
from core.models import ChatSession

def map_role(sender):
    # Gemini expects 'user' or 'model'
    return 'user' if sender == 'user' else 'model'

# Retrieve or start a chat session for a user
def create_session(user_id, hr_level_id):
    session = ChatSession(
        id=str(uuid.uuid4()),
        user_id=user_id,
        hr_level_id=hr_level_id
    )
    db.session.add(session)
    db.session.commit()
    return session

def strip_json(text):
    """
    Strip any ```json fences and extract the first JSON object.
    """
    text = re.sub(r'```(?:json)?', '', text)
    m    = re.search(r'\{.*\}', text, flags=re.DOTALL)
    return m.group(0).strip() if m else text

def build_system_prompt(hr_level, job_type, asked_nums, first_question_only=False, current_qnum=None):
    """
    hr_level: HRLevel instance
    job_type: str
    asked_nums: list of ints already asked
    first_question_only: bool, True if we're still on Q1
    current_qnum: the number of the last question asked (>=2)
    """
    tone_map = {
        1: ("hangat dan suportif", (3, 5)),
        2: ("netral dan profesional", (5, 7)),
        3: ("sarkastik dan menantang serta senioritas tinggi", (7, 10)),
    }
    tone, (low, high) = tone_map[hr_level.difficulty_rank]

    # If still on the very first question, just ask
    if first_question_only:
        return (
            f"Anda adalah pewawancara HR untuk posisi {job_type} dengan nada {tone}.\n\n"
            f"Pilih satu pertanyaan baru yang belum pernah Anda ajukan dari pool {low}–{high} pertanyaan.\n\n"
            "OUTPUT ONLY RAW JSON dalam format:\n"
            "{\n"
            '  "type": "question",\n'
            '  "question_number": <integer>,\n'
            '  "question_text": "…"\n'
            "}\n"
        )

    # Otherwise, enforce feedback/end constraints
    feedback_variants = [
        "Jawaban Anda belum tepat, tolong fokus menjawab pertanyaan.",
        "Maaf, jawaban itu tidak relevan—mari serius sedikit.",
        "Sepertinya Anda keluar konteks; tolong jawab sesuai pertanyaan.",
        "Tolong kembali ke pokok soal dan jawab pertanyaannya.",
        "Itu belum menjawab pertanyaan—mohon jawab langsung pertanyaannya."
    ]
    fb_text = rd.choice(feedback_variants)
    prev = f"Anda sudah mengajukan pertanyaan bernomor {asked_nums}. Jangan ulangi lagi. " if asked_nums else ""

    return (
        f"Anda adalah pewawancara HR untuk posisi {job_type} dengan nada {tone}.\n\n"
        "1) Sebelum mengajukan pertanyaan baru, periksa pesan terakhir user:\n"
        "- Jika TIDAK benar-benar menjawab pertanyaan JSON Anda sebelumnya (off-topic, kosong, atau tidak terkait):\n"
        "  a) Jika ini kali ketiga user gagal menjawab pertanyaan yang SAMA, keluarkan RAW JSON:\n"
        "{\n"
        '  "type": "end",\n'
        '  "score": <angka 1–10>,\n'
        '  "recommendations": ["…","…"]\n'
        "}\n"
        "     lalu hentikan sesi.\n\n"
        "  b) Jika belum ketiga kali, keluarkan RAW JSON feedback:\n"
        "{\n"
        '  "type": "feedback",\n'
        f'  "feedback_text": "{fb_text}"\n'
        "}\n\n"
        f"2) Jika jawaban relevan, acak satu pertanyaan baru dari pool {low}–{high}. {prev}\n"
        "   OUTPUT ONLY RAW JSON dalam format:\n"
        "{\n"
        '  "type": "question",\n'
        '  "question_number": <integer>,\n'
        '  "question_text": "…"\n'
        "}\n"
    )
