import uuid
import os
import dotenv

from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy

from core.generate import generate_response
from core.cv_analyzer import save_submission_file, generate_cv_json

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

from core.course_enroll import (
    enroll_course, unenroll_course,
    complete_course, list_user_enrollments
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

    return jsonify({'message': 'Login successful.',}), 200

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
def build_system_prompt(hr_level, job_type):
    rank = hr_level.difficulty_rank
    if rank == 1:
        return (
            f"You are an HR interviewer conducting a relaxed, entry-level interview for the position of {job_type}. "
                "Your goal is to help the candidate feel comfortable and highlight their basic skills and personality. "
                "Ask 3 to 5 (one by one, wait until the candidate answers the questions given tough questions)"
                "Keep your tone warm, supportive, and encouraging throughout the conversation."
        )
    elif rank == 2:
        return (
            f"You are an HR interviewer for the position of {job_type}, conducting a standard professional interview. "
                "Ask 5 to 7 (one by one wait, until the candidate answers the questions given tough questions) balanced questions that probe both behavioral and technical competencies"
                "Maintain a respectful, neutral tone—professional but not intimidating."
        )
    else:
        return (
            f"You are an HR interviewer for the position of {job_type}. Assume a subtly sarcastic and challenging demeanor to create a tense atmosphere. "
                "Your aim is to test the candidate’s composure under pressure and make them work hard to impress you. Ask 7 to 10 (one by one, wait until the candidate answers the questions given tough questions)"
                "Use ironic remarks and maintain a controlled, critical tone to keep the candidate on edge throughout the interview."
        )

@app.route('/api/v1/hr_levels', methods=['GET'])
def list_hr_levels():
    levels = HRLevel.query.order_by(HRLevel.difficulty_rank).all()
    return jsonify([l.to_dict() for l in levels]), 200

@app.route('/api/v1/feature/interview/chat', methods=['POST'])
def chat():
    data      = request.get_json() or {}
    sid    = data.get('session_id')
    uid    = data.get('user_id')
    text   = data.get('message')
    hrid   = data.get('hr_level_id')
    job    = data.get('job_type')
    evalf  = data.get('evaluate', False)

    # 1) INITIAL CALL: start session + send “system” prompt as a user‐role dict
    if not sid and not evalf:
        # … validate uid/hrid/job/text …
        session = ChatSession(id=str(uuid.uuid4()), user_id=uid, hr_level_id=hrid)
        db.session.add(session); db.session.commit()
        db.session.add(ChatMessage(session_id=session.id, sender='user', message=f"[Job: {job}] {text}"))
        db.session.commit()

        lvl = HRLevel.query.get(hrid)
        system_prompt = build_system_prompt(lvl, job)

        messages = [
            { "role": "user",  "content": system_prompt }
        ]

    # 2) EVALUATION CALL: final assessment
    elif evalf and sid:
        session = ChatSession.query.get(sid)
        history = ChatMessage.query.filter_by(session_id=sid).order_by(ChatMessage.sent_at).all()

        eval_prompt = (
          "Now that the interview is complete, review ALL candidate responses and reply exactly:\n\n"
          "Skor: <1-10>\n"
          "Rekomendasi:\n"
          "- <item1>\n"
          "- <item2>\n"
        )
        messages = [{ "role": "user", "content": eval_prompt }]
        for m in history:
            messages.append({
                "role": "user" if m.sender=="user" else "model",
                "content": m.message
            })

        out = generate_response(messages)
        return jsonify({"session_id": sid, "evaluation": out}), 200

    # 3) CONTINUE INTERVIEW: save answer & get next question
    else:
        session = ChatSession.query.get(sid)
        db.session.add(ChatMessage(session_id=sid, sender='user', message=text))
        db.session.commit()
        messages = []

    # append FULL history for context in every non‐eval call
    history = ChatMessage.query.filter_by(session_id=session.id).order_by(ChatMessage.sent_at).all()
    for m in history:
        messages.append({
            "role": "user" if m.sender=="user" else "model",
            "content": m.message
        })

    # call Gemini
    try:
        reply = generate_response(messages)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # save the AI’s next question
    if not evalf:
        db.session.add(ChatMessage(session_id=session.id, sender='bot', message=reply))
        db.session.commit()

    return jsonify({'session_id': session.id, 'response': reply}), 200

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
