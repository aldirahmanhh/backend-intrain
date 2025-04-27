import uuid
import os
import dotenv
import re
import json
import random

from flask import Flask, request, jsonify, abort
from datetime import datetime

from core.chat import strip_json, build_system_prompt
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
    ChatSession, ChatMessage, ChatEvaluation,
    CVSubmission, CVReview, CVReviewSection,
    WorkExperience,
    CourseEnrollment, Course, Job
)

# Create tables immediately to ensure schema is in place
with app.app_context():
    db.create_all()

# Utility to serialize SQLAlchemy models
def serialize(obj):
    return obj.to_dict() if hasattr(obj, 'to_dict') else {}

# -------------------- Server Endpoints --------------------

# Root Endpoint
@app.route('/')
def index():
    return "Server is Online!"

# Health Check Endpoint
@app.route('/api/v1/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

# -------------------- User Data Endpoints --------------------

# User Registration
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

# User Login
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

# User Update
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

# -------------------- HR Chatbot API Endpoints --------------------

# List HR Levels
@app.route('/api/v1/feature/chat/hr_levels', methods=['GET'])
def list_hr_levels():
    levels = HRLevel.query.order_by(HRLevel.difficulty_rank).all()
    payload = [level.to_dict() for level in levels]
    return jsonify(payload), 200

# HR Chatbot API
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

    # 2) Continue Chat: save answer, then either ask next or evaluate
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

    # If done with all questions → evaluate
    if len(asked) >= session.total_questions:
        # Build the AI prompt
        eval_prompt = (
            "You are an expert HR evaluator. Now that the interview is complete, "
            "review ALL candidate responses and OUTPUT ONLY RAW JSON in this exact format "
            "(no markdown, no fences):\n\n"
            "{\n"
            '  "score": <integer 1-10>,\n'
            '  "recommendations": [\n'
            '    "…",\n'
            '    "…"\n'
            '  ]\n'
            "}\n"
        )

        # Assemble messages for Gemini
        msgs = [{ "role": "system", "content": eval_prompt }]
        for m in history:
            msgs.append({
                "role": "user" if m.sender == 'user' else "model",
                "content": m.message
            })

        # call the AI
        ai_out  = generate_response(msgs)
        raw     = strip_json(ai_out)
        result  = json.loads(raw)

        # Save the evaluation
        rec = ChatEvaluation(
            session_id      = session.id,
            score           = result['score'],
            recommendations = json.dumps(result['recommendations'])
        )
        db.session.add(rec)
        db.session.commit()

        # Return the saved evaluation
        return jsonify({
            'session_id': session.id,
            'evaluation': rec.to_dict()
        }), 200

    # Else: ask next question
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

# Chat History
@app.route('/api/v1/feature/interview/chat/history/<user_id>', methods=['GET'])
def list_user_chats(user_id):
    """
    Returns all chat sessions for a given user, ordered by most recent activity.
    """
    # Fetch all sessions for this user
    sessions = (
        ChatSession
        .query
        .filter_by(user_id=user_id)
        .order_by(ChatSession.started_at.desc())
        .all()
    )

    chats = []
    for s in sessions:
        # Get the latest message in the session
        last_msg = (
            ChatMessage
            .query
            .filter_by(session_id=s.id)
            .order_by(ChatMessage.sent_at.desc())
            .first()
        )

        if last_msg:
            content = last_msg.message
            if last_msg.sender == 'bot':
                try:
                    # Strip any ``` fences and parse JSON
                    blob = json.loads(re.sub(r'```(?:json)?', '', content))
                    snippet = blob.get('question_text') or blob.get('answer_text') or content
                except:
                    snippet = content
            else:
                snippet = content

            last_seen = last_msg.sent_at.isoformat()
        else:
            snippet, last_seen = None, None

        chats.append({
            'session_id':      s.id,
            'job_type':        s.job_type,
            'hr_level_id':     s.hr_level_id,
            'started_at':      s.started_at.isoformat(),
            'last_message':    snippet,
            'last_message_at': last_seen
        })

    return jsonify({'user_id': user_id, 'chats': chats}), 200

# Chat Sessions History
@app.route('/api/v1/feature/interview/chat/<session_id>/history', methods=['GET'])
def get_history(session_id):
    msgs = ChatMessage.query.filter_by(session_id=session_id)\
                             .order_by(ChatMessage.sent_at).all()
    history = []
    for m in msgs:
        if m.sender == 'bot':
            try:
                content = json.loads(strip_json(m.message))
            except:
                content = {'raw': m.message}
        else:
            content = {'text': m.message}
        history.append({
            'sender':  m.sender,
            'content': content,
            'sent_at': m.sent_at.isoformat()
        })
    return jsonify({'session_id': session_id, 'history': history}), 200

# -------------------- CV Upload & Review Endpoints --------------------

# CV Upload
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


# List CV Reviews History
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

# Get One CV Submission History
@app.route('/api/v1/feature/cv/history/<submission_id>', methods=['GET'])
def cv_history(submission_id):
    from core.models import CVSubmission
    sub = CVSubmission.query.get(submission_id)
    if not sub:
        return jsonify(error='Submission not found'), 404
    return jsonify(submission=sub.to_dict()), 200

# List Reviewed CV History
@app.route('/api/v1/feature/cv/history/user/<user_id>', methods=['GET'])
def cv_history_user(user_id):
    from core.models import CVSubmission
    subs = CVSubmission.query.filter_by(user_id=user_id).all()
    return jsonify([s.to_dict() for s in subs]), 200


# -------------------- Course Enrollment Endpoints --------------------

# List All Courses
@app.route('/api/v1/feature/courses', methods=['GET'])
def api_list_courses():
    courses = Course.query.order_by(Course.created_at.desc()).all()
    return jsonify([c.to_dict() for c in courses]), 200

# Get a Specific Course
@app.route('/api/v1/feature/courses/<string:course_id>', methods=['GET'])
def api_get_course(course_id):
    # look up the Course by its UUID
    course = get_course(course_id)
    if course is None:
        return jsonify({'error': 'Course not found'}), 404

    # return its serialized form
    return jsonify(course.to_dict()), 200

# Enroll a Course
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

# Unenroll from a Course
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


# Mark Course as Completed
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

# List a User's Enrollments
@app.route('/api/v1/feature/courses/user/<user_id>/enrollments', methods=['GET'])
def api_list_user_courses(user_id):
    if not User.query.get(user_id):
        return jsonify({'error':'User not found'}), 404

    enrolls = list_user_enrollments(user_id)
    return jsonify([e.to_dict() for e in enrolls]), 200

# ---------- Work Experience Endpoints ----------

# List all work experiences for a user
@app.route('/api/v1/users/<string:user_id>/work_experiences', methods=['GET'])
def list_work_experiences(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(404, description='User not found')
    exps = (
        WorkExperience
        .query
        .filter_by(user_id=user_id)
        .order_by(WorkExperience.start_year.desc(), WorkExperience.start_month.desc())
        .all()
    )
    return jsonify([exp.to_dict() for exp in exps])

# Retrieve a single work experience
@app.route('/api/v1/users/<string:user_id>/work_experiences/<string:exp_id>', methods=['GET'])
def get_work_experience(user_id, exp_id):
    exp = WorkExperience.query.filter_by(id=exp_id, user_id=user_id).first()
    if not exp:
        abort(404, description='Experience not found')
    return jsonify(exp.to_dict())

# Create a new work experience
@app.route('/api/v1/users/<string:user_id>/work_experiences', methods=['POST'])
def create_work_experience(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(404, description='User not found')
    data = request.get_json() or {}
    required_fields = ['job_title', 'company_name', 'start_month', 'start_year']
    for field in required_fields:
        if field not in data:
            abort(400, description=f"'{field}' is required")

    exp = WorkExperience(
        id=str(uuid.uuid4()),
        user_id=user_id,
        job_title=data['job_title'],
        company_name=data['company_name'],
        job_desc=data.get('job_desc'),
        start_month=data['start_month'],
        start_year=data['start_year'],
        end_month=data.get('end_month'),
        end_year=data.get('end_year'),
        is_current=data.get('is_current', False),
        created_at=datetime.utcnow()
    )
    db.session.add(exp)
    db.session.commit()
    return jsonify(exp.to_dict()), 201

# Update an existing work experience
@app.route('/api/v1/users/<string:user_id>/work_experiences/<string:exp_id>', methods=['PUT'])
def update_work_experience(user_id, exp_id):
    exp = WorkExperience.query.filter_by(id=exp_id, user_id=user_id).first()
    if not exp:
        abort(404, description='Experience not found')
    data = request.get_json() or {}
    updatable = ['job_title', 'company_name', 'job_desc', 'start_month', 'start_year', 'end_month', 'end_year', 'is_current']
    for field in updatable:
        if field in data:
            setattr(exp, field, data[field])
    db.session.commit()
    return jsonify(exp.to_dict())

# Delete a work experience
@app.route('/api/v1/users/<string:user_id>/work_experiences/<string:exp_id>', methods=['DELETE'])
def delete_work_experience(user_id, exp_id):
    exp = WorkExperience.query.filter_by(id=exp_id, user_id=user_id).first()
    if not exp:
        abort(404, description='Experience not found')
    db.session.delete(exp)
    db.session.commit()
    return jsonify({'message':'Experience deleted'}), 200

# List all jobs
@app.route('/api/v1/jobs', methods=['GET'])
def list_jobs():
    jobs = Job.query.order_by(Job.posted_at.desc()).all()
    return jsonify([job.to_dict() for job in jobs])

if __name__ == '__main__':
    app.run(debug=True)