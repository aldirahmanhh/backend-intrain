import uuid
import os
import dotenv
import re
import json
import random

from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy

from core.generate import generate_response
from core.cv_analyzer import save_submission_file, generate_cv_json
from core.course import get_course
from core.course_enroll import (
    enroll_course, unenroll_course,
    complete_course, list_user_enrollments
)

dotenv.load_dotenv()

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
from core.db import db

# Bind db to this Flask app
db.init_app(app)

# Import models after db is initialized after db is initialized
from core.models import (
    User, HRLevel,
    ChatSession, ChatMessage,
    CVSubmission, CVReview, CVReviewSection,
    CourseEnrollment, Course, Job
)

# Create tables immediately to ensure schema is in place
with app.app_context():
    db.create_all()

# Utility to serialize SQLAlchemy models
def serialize(obj):
    return obj.to_dict() if hasattr(obj, 'to_dict') else {}

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

# Root Endpoint
@app.route('/')
def index():
    return "Server is Online!"

# Health Check Endpoint
@app.route('/api/v1/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

# User Data Endpoints
@app.route('/api/v1/auth/user/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Parameters username and password are required.'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username is already registered.'}), 400

    user = User(
        id=str(uuid.uuid4()),
        username=username,
        password=password,
        name=data.get('name', ''),
        email=data.get('email', '')
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Registration successful.',}), 201

@app.route('/api/v1/auth/user/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Parameters username and password are required.'}), 400

    user = User.query.filter_by(username=username, password=password).first()
    if not user:
        return jsonify({'error': 'Incorrect username or password.'}), 401

    return jsonify({'message': 'Login successful.', 'user': serialize(user)}), 200

@app.route('/api/v1/auth/user/update', methods=['PUT'])
def update_user():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'Parameter user_id is required.'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found.'}), 404

    for field in ['username', 'password', 'name', 'email']:
        if field in data:
            setattr(user, field, data[field])
    db.session.commit()

    return jsonify({'message': 'User data updated successfully.',}), 200

# HR Chatbot API Endpoints
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

# Routes
@app.route('/api/v1/hr_levels', methods=['GET'])
def list_hr_levels():
    levels = HRLevel.query.order_by(HRLevel.difficulty_rank).all()
    return jsonify([l.__dict__ for l in levels]), 200

@app.route('/api/v1/feature/interview/chat', methods=['POST'])
def chat():
    data      = request.get_json() or {}
    sid       = data.get('session_id')
    user_text = data.get('message')

    # 1) INITIAL CALL: no session_id → create session & ask intro
    if not sid:
        uid   = data['user_id']
        hrid  = data['hr_level_id']
        job   = data['job_type']

        # decide how many real questions (excluding intro)
        low, high = {1:(3,5), 2:(5,7), 3:(7,10)}[HRLevel.query.get(hrid).difficulty_rank]
        n_real    = random.randint(low, high)

        session = ChatSession(
            user_id         = uid,
            hr_level_id     = hrid,
            job_type        = job,
            total_questions = n_real + 1   # +1 for the intro question
        )
        db.session.add(session)
        db.session.commit()

        # send intro as question #1
        intro_q = {
            "type": "question",
            "question_number": 1,
            "question_text": (
                "Please introduce yourself: your name, current role, "
                "and how many years of experience you have."
            )
        }
        db.session.add(ChatMessage(
            session_id=session.id,
            sender='bot',
            message=json.dumps(intro_q)
        ))
        db.session.commit()

        return jsonify({"session_id": session.id, "response": intro_q}), 200

    # 2) CONTINUE CALL: save answer, then either ask next or evaluate
    session = ChatSession.query.get(sid)
    db.session.add(ChatMessage(
        session_id=sid,
        sender='user',
        message=user_text
    ))
    db.session.commit()

    # reconstruct history & track asked questions
    history = ChatMessage.query.filter_by(session_id=sid).order_by(ChatMessage.sent_at).all()
    asked   = []
    for msg in history:
        if msg.sender == 'bot':
            try:
                blk = strip_json(msg.message)
                q   = json.loads(blk)
                if q.get("type") == "question":
                    asked.append(q["question_number"])
            except:
                pass

    # if done with all questions → evaluate
    if len(asked) >= session.total_questions:
        eval_p = (
            "You are an expert HR evaluator. Now that the interview is complete, review ALL candidate responses "
            "and OUTPUT ONLY RAW JSON in this exact format (no markdown, no fences):\n"
            "{\n"
            '  "score": <integer 1-10>,\n'
            '  "recommendations": [\n'
            '    "…",\n'
            '    "…"\n'
            '  ]\n'
            "}\n"
        )
        msgs = [{ "role": "system", "content": eval_p }]
        for m in history:
            msgs.append({
                "role": "user" if m.sender=="user" else "model",
                "content": m.message
            })
        out   = generate_response(msgs)
        clean = strip_json(out)
        eval_json = json.loads(clean)
        return jsonify({"session_id": sid, "evaluation": eval_json}), 200

    # else → ask next question
    lvl   = HRLevel.query.get(session.hr_level_id)
    sys_p = build_system_prompt(lvl, session.job_type, asked)
    msgs  = [{ "role": "system", "content": sys_p }]
    for m in history:
        msgs.append({
            "role": "user" if m.sender=="user" else "model",
            "content": m.message
        })

    out   = generate_response(msgs)
    clean = strip_json(out)
    question = json.loads(clean)

    db.session.add(ChatMessage(
        session_id=sid,
        sender='bot',
        message=clean
    ))
    db.session.commit()

    return jsonify({"session_id": sid, "response": question}), 200

# CV
@app.route('/api/v1/feature/cv/upload', methods=['POST'])
def upload_cv():
    file    = request.files.get('file')
    user_id = request.form.get('user_id')
    if not user_id or not file:
        return jsonify({'error': 'user_id and file are required.'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found.'}), 404

    # 1) Save the uploaded file and create CVSubmission
    try:
        submission = save_submission_file(file, user_id)
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400

    # 2) Run the AI screener, get back a dict with ats_passed, overall_feedback, sections[]
    try:
        screening = generate_cv_json(submission)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # 3) Persist CVReview
    review = CVReview(
        id=str(uuid.uuid4()),
        submission_id=submission.id,
        ats_passed=screening['ats_passed'],
        overall_feedback=screening['overall_feedback']
    )
    db.session.add(review)
    db.session.commit()

    # 4) Persist each CVReviewSection
    section_objs = []
    for sec in screening.get('sections', []):
        obj = CVReviewSection(
            id=str(uuid.uuid4()),
            review_id=review.id,
            section=sec['section'],
            needs_improvement=sec['needs_improvement'],
            feedback=sec['feedback']
        )
        db.session.add(obj)
        section_objs.append(obj)
    db.session.commit()

    # 5) Return everything as JSON
    return jsonify({
        'submission': submission.to_dict(),
        'review':     review.to_dict(),
        'sections':   [o.to_dict() for o in section_objs]
    }), 200

@app.route('/api/v1/feature/cv/history/user/<user_id>/reviews', methods=['GET'])
def user_cv_reviews(user_id):
    # 1) Verify the user exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found.'}), 404

    # 2) Load all submissions for this user, newest first
    submissions = (CVSubmission.query
                   .filter_by(user_id=user_id)
                   .order_by(CVSubmission.uploaded_at.desc())
                   .all())

    history = []
    for sub in submissions:
        # 3) Find the review (if any)
        review = CVReview.query.filter_by(submission_id=sub.id).first()
        if not review:
            # no review yet—skip or include empty placeholder
            history.append({
                'submission': sub.to_dict(),
                'review':     None,
                'sections':   []
            })
            continue

        # 4) Load all section feedback for that review
        sections = (CVReviewSection.query
                    .filter_by(review_id=review.id)
                    .all())

        history.append({
            'submission': sub.to_dict(),
            'review':     review.to_dict(),
            'sections':   [s.to_dict() for s in sections]
        })

    return jsonify(history), 200

@app.route('/api/v1/feature/cv/history/<submission_id>', methods=['GET'])
def cv_history(submission_id):
    from core.models import CVSubmission
    sub = CVSubmission.query.get(submission_id)
    if not sub:
        return jsonify(error='Submission not found'), 404
    return jsonify(submission=sub.to_dict()), 200

@app.route('/api/v1/feature/cv/history/user/<user_id>', methods=['GET'])
def cv_history_user(user_id):
    from core.models import CVSubmission
    subs = CVSubmission.query.filter_by(user_id=user_id).all()
    return jsonify([s.to_dict() for s in subs]), 200


# Course Enrollment Endpoints

@app.route('/api/v1/feature/courses', methods=['GET'])
def api_list_courses():
    courses = Course.query.order_by(Course.created_at.desc()).all()
    return jsonify([c.to_dict() for c in courses]), 200

@app.route('/api/v1/feature/courses/<string:course_id>', methods=['GET'])
def api_get_course(course_id):
    # look up the Course by its UUID
    course = get_course(course_id)
    if course is None:
        return jsonify({'error': 'Course not found'}), 404

    # return its serialized form
    return jsonify(course.to_dict()), 200

# 1) Enroll in a course
@app.route('/api/v1/feature/courses/enroll', methods=['POST'])
def api_enroll_course():
    data      = request.get_json() or {}
    user_id   = data.get('user_id')
    course_id = data.get('course_id')
    if not user_id or not course_id:
        return jsonify({'error':'user_id & course_id required'}), 400

    # validate user & course exist
    if not User.query.get(user_id):
        return jsonify({'error':'User not found'}), 404
    if not Course.query.get(course_id):
        return jsonify({'error':'Course not found'}), 404

    enroll = enroll_course(user_id, course_id)
    if enroll is None:
        return jsonify({'message':'Already enrolled'}), 200

    return jsonify(enroll.to_dict()), 201


# 2) Unenroll from a course
@app.route('/api/v1/feature/courses/unenroll', methods=['POST'])
def api_unenroll_course():
    data      = request.get_json() or {}
    user_id   = data.get('user_id')
    course_id = data.get('course_id')
    if not user_id or not course_id:
        return jsonify({'error':'user_id & course_id required'}), 400

    if unenroll_course(user_id, course_id):
        return jsonify({'message':'Unenrolled successfully'}), 200
    return jsonify({'error':'Enrollment not found'}), 404


# 3) Mark course as completed
@app.route('/api/v1/feature/courses/complete', methods=['POST'])
def api_complete_course():
    data      = request.get_json() or {}
    user_id   = data.get('user_id')
    course_id = data.get('course_id')
    if not user_id or not course_id:
        return jsonify({'error':'user_id & course_id required'}), 400

    updated = complete_course(user_id, course_id)
    if not updated:
        return jsonify({'error':'Enrollment not found'}), 404
    return jsonify(updated.to_dict()), 200


# 4) List a user's enrollments
@app.route('/api/v1/feature/courses/user/<user_id>/enrollments', methods=['GET'])
def api_list_user_courses(user_id):
    if not User.query.get(user_id):
        return jsonify({'error':'User not found'}), 404

    enrolls = list_user_enrollments(user_id)
    return jsonify([e.to_dict() for e in enrolls]), 200


if __name__ == '__main__':

    app.run(debug=True)