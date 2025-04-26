
import uuid
import re

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
    Instruct Gemini to output exactly one JSON question,
    never repeating any in asked_nums.
    """
    tone_map = {
        1: ("warm, supportive", (3, 5)),
        2: ("neutral, professional", (5, 7)),
        3: ("subtly sarcastic and challenging", (7, 10)),
    }
    tone, (low, high) = tone_map[hr_level.difficulty_rank]

    prev = ""
    if asked_nums:
        prev = f"You have already asked questions numbered {asked_nums}. Do not repeat them. "

    return (
        f"You are an HR interviewer for the {job_type} position in a {tone} tone. "
        f"Randomly select one new question from your pool of {low}–{high} job-related questions. {prev}\n\n"
        "OUTPUT ONLY RAW JSON in this exact format (no markdown, no fences):\n"
        "{\n"
        '  "type": "question",\n'
        '  "question_number": <integer>,\n'
        '  "question_text": "…"\n'
        "}\n"
    )