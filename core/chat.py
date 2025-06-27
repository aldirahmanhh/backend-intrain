
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

def build_system_prompt(hr_level, job_type, asked_nums):
    """
    Instruksikan model untuk:
    1) Cek apakah pesan terakhir user benar-benar menjawab pertanyaan sebelumnya.
       - Jika TIDAK, berikan hanya RAW JSON feedback dengan satu variasi pesan secara acak.
       - Jika ini ketiga kalinya user gagal menjawab pertanyaan yang SAMA, keluarkan RAW JSON untuk
         mengakhiri sesi dengan skor dan rekomendasi, lalu hentikan sesi.
    2) Jika jawabannya relevan, keluarkan pertanyaan baru dalam format JSON seperti biasa.
    """
    tone_map = {
        1: ("hangat dan suportif", (3, 5)),
        2: ("netral dan profesional", (5, 7)),
        3: ("sarkastik dan menantang serta senioritas tinggi", (7, 10)),
    }
    tone, (low, high) = tone_map[hr_level.difficulty_rank]

    feedback_variants = [
        "Jawaban Anda belum tepat, tolong fokus menjawab pertanyaan.",
        "Maaf, jawaban itu tidak relevan—mari serius sedikit.",
        "Sepertinya Anda keluar konteks; tolong jawab sesuai pertanyaan.",
        "Tolong kembali ke pokok soal dan jawab pertanyaannya.",
        "Itu belum menjawab pertanyaan—mohon jawab langsung pertanyaannya."
    ]
    feedback_list_str = json.dumps(rd.choice(feedback_variants), ensure_ascii=False)

    prev = f"Anda sudah mengajukan pertanyaan bernomor {asked_nums}. Jangan ulangi lagi. " if asked_nums else ""

    return (
        f"Anda adalah pewawancara HR untuk posisi {job_type} dengan nada {tone}.\n\n"
        "1) Sebelum mengajukan pertanyaan baru, periksa pesan terakhir user:\n"
        "- Jika TIDAK benar-benar menjawab pertanyaan JSON Anda sebelumnya (off-topic, kosong, atau tidak terkait), maka:\n"
        "  a) Jika ini kali ketiga user gagal menjawab pertanyaan yang SAMA, keluarkan hanya RAW JSON:\n"
        "     {\n"
        '       "type": "end",\n'
        '       "score": <angka 1–10>,\n'
        '       "recommendations": [ "…", "…" ]\n'
        "     }\n"
        "     dan hentikan sesi.\n\n"
        "  b) Jika belum ketiga kali, keluarkan hanya RAW JSON feedback dalam format ini:\n"
        "{\n"
        '  "type": "feedback",\n'
        '  "feedback_text": "<salah satu dari berikut>"\n'
        "}\n\n"
        f"     Di mana <salah satu dari berikut> dipilih acak dari:\n"
        f"{feedback_list_str}\n\n"
        "2) Jika jawaban relevan, acak satu pertanyaan baru dari pool "
        f"{low}–{high} pertanyaan terkait {job_type}. {prev}\n"
        "   Keluarkan hanya RAW JSON dalam format ini:\n"
        "{\n"
        '  "type": "question",\n'
        '  "question_number": <integer>,\n'
        '  "question_text": "…"\n'
        "}\n"
    )
