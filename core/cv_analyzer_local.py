import os
import uuid
import json
import re
import PyPDF2
from werkzeug.utils import secure_filename
from core.generate import generate_response
from core.models import CVSubmission
from core.db import db

UPLOAD_DIR  = os.getenv('UPLOAD_DIR', 'uploads')
ALLOWED_EXT = {'pdf', 'png', 'jpg', 'jpeg'}
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_submission_file(file_storage, user_id):
    filename = secure_filename(file_storage.filename)
    ext = filename.rsplit('.', 1)[-1].lower()
    if ext not in ALLOWED_EXT:
        raise ValueError(f"File type .{ext} not supported.")
    unique_name = f"{uuid.uuid4()}.{ext}"
    path = os.path.join(UPLOAD_DIR, unique_name)
    file_storage.save(path)

    sub = CVSubmission(
        id=str(uuid.uuid4()),
        user_id=user_id,
        file_name=filename,
        file_type=ext,
        file_url=path
    )
    db.session.add(sub)
    db.session.commit()
    return sub

def extract_text_from_cv(filepath):
    ext = filepath.rsplit('.', 1)[-1].lower()
    if ext == 'pdf':
        text = ""
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text
    return f"[Non-PDF CV: please OCR {os.path.basename(filepath)}]"

def generate_cv_json(submission):
    """
    Prompts Gemini to return ONLY raw JSON:
      { "ats_passed":bool, "overall_feedback":str, "sections":[{...},…] }
    Strips any code fences, parses and returns the dict.
    """
    text = extract_text_from_cv(submission.file_url)
    prompt = (
        "You are an expert HR screener. Given the CV content below, decide if it passes an ATS, "
        "and for each section (profile_summary, education, experience, skills, certification, portfolio) "
        "indicate needs_improvement (true/false) and provide feedback. "
        "OUTPUT ONLY RAW JSON in this exact format (no markdown, no fences):\n\n"
        "{\n"
        "  \"ats_passed\": true|false,\n"
        "  \"overall_feedback\": \"…\",\n"
        "  \"sections\": [\n"
        "    {\"section\":\"profile_summary\",\"needs_improvement\":true,\"feedback\":\"…\"},\n"
        "    …\n"
        "  ]\n"
        "}\n\n"
        f"CV TEXT:\n\n{text}"
    )
    ai_out = generate_response([prompt])

    # strip ``` fences if any, then grab the JSON object
    cleaned = re.sub(r"```(?:json)?", "", ai_out).strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise RuntimeError(f"Invalid JSON from screener:\n{ai_out}")
    json_str = match.group(0)

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"JSON parse error: {e.msg}\nRaw output:\n{ai_out}")

    return data
