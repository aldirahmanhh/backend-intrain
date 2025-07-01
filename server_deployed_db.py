import uuid
import os
import dotenv
import re
import json
import random
import random as rd
import sqlalchemy
import pymysql
import certifi

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
from werkzeug.security import generate_password_hash

dotenv.load_dotenv()

app = Flask(__name__)

host     = os.getenv('AZURE_MYSQL_HOST')
port     = os.getenv('AZURE_MYSQL_PORT', '3306')
user     = os.getenv('AZURE_MYSQL_USER')
password = os.getenv('AZURE_MYSQL_PASS')
db_name  = os.getenv('AZURE_MYSQL_DB')

DATABASE_URL = (
    f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"
    "?charset=utf8mb4"
)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Engine options untuk SSL
app.config['SQLALCHEMY_DATABASE_URI']        = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS']      = {
    'connect_args': {
        'ssl': {
            # pakai CA bundle dari certifi
            'ca': certifi.where()
        }
    }
}

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
    Roadmap, RoadmapStep,
    UserRoadmap, UserRoadmapProgress, Achievement,
    CourseEnrollment, Course, Job, MentorProfile, MentorAvailability,
    MentorshipSession, MentorshipFeedback
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
    raw_pw   = data.get('password')
    if not username or not raw_pw:
        return jsonify({'error': 'Parameters username and password are required.'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username is already registered.'}), 400

    # hash the password
    hashed_pw = generate_password_hash(raw_pw)

    user = User(
        id=str(uuid.uuid4()),
        username=username,
        password=hashed_pw,
        name=data.get('name', ''),
        email=data.get('email', '')
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Registration successful.'}), 201


# User Login
from werkzeug.security import check_password_hash
# …

@app.route('/api/v1/auth/user/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    raw_pw   = data.get('password')
    if not username or not raw_pw:
        return jsonify({'error': 'Parameters username and password are required.'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, raw_pw):
        return jsonify({'error': 'Incorrect username or password.'}), 401

    return jsonify({'message': 'Login successful.', 'user': user.to_dict()}), 200


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

    # 1) INITIAL CALL: start session + intro question
    if not sid:
        uid   = data['user_id']
        hrid  = data['hr_level_id']
        job   = data['job_type']
        lvl   = HRLevel.query.get(hrid)
        low, high = {1:(3,5),2:(5,7),3:(7,10)}[lvl.difficulty_rank]
        n_real = rd.randint(low, high)

        session = ChatSession(
            id=str(uuid.uuid4()),
            user_id=uid,
            hr_level_id=hrid,
            job_type=job,
            total_questions=n_real+1
        )
        db.session.add(session)
        db.session.commit()

        intro_q = {
            "type": "question",
            "question_number": 1,
            "question_text": (
                "Perkenalkan diri Anda: nama, peran saat ini, "
                "dan berapa tahun pengalaman yang Anda miliki."
            )
        }
        db.session.add(ChatMessage(
            session_id=session.id,
            sender='bot',
            message=json.dumps(intro_q)
        ))
        db.session.commit()

        return jsonify({"session_id": session.id, "response": intro_q}), 200

    # 2) CONTINUATION: save user answer
    session = ChatSession.query.get(sid) or abort(404, "Session not found")
    db.session.add(ChatMessage(
        session_id=sid,
        sender='user',
        message=user_text
    ))
    db.session.commit()

    # rebuild history & asked list
    history = ChatMessage.query.filter_by(session_id=sid).order_by(ChatMessage.sent_at).all()
    asked = []
    for m in history:
        if m.sender=='bot':
            try:
                blk = strip_json(m.message)
                q   = json.loads(blk)
                if q.get("type")=="question":
                    asked.append(q["question_number"])
            except:
                pass

    # detect last question number (for constraints)
    last_qnum = None
    for m in reversed(history):
        if m.sender=='bot':
            try:
                p = json.loads(strip_json(m.message))
                if p.get("type")=="question":
                    last_qnum = p["question_number"]
                    break
            except:
                pass

    # 3) If we've asked all questions, request evaluation
    if len(asked) >= session.total_questions:
        eval_prompt = (
            "Anda adalah evaluator HR yang ahli. Wawancara selesai, "
            "Tinjau SEMUA jawaban kandidat dan OUTPUT ONLY RAW JSON:\n\n"
            "{\n"
            '  "type": "end",\n'
            '  "score": <angka 1–10>,\n'
            '  "recommendations": ["…","…"]\n'
            "}\n"
        )
        msgs = [{"role":"system","content":eval_prompt}]
        for m in history:
            msgs.append({
                "role": "user" if m.sender=='user' else "model",
                "content": m.message
            })

        ai_out = generate_response(msgs)
        result = json.loads(strip_json(ai_out))

        # As soon as we get a type=end, wrap & persist
        if result.get("type") == "end":
            eval_id   = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()

            # save to DB
            rec = ChatEvaluation(
                id               = eval_id,
                session_id       = sid,
                score            = result["score"],
                recommendations  = json.dumps(result["recommendations"]),
                evaluated_at     = timestamp
            )
            db.session.add(rec)
            db.session.commit()

            return jsonify({
                "evaluation": {
                    "id":               eval_id,
                    "session_id":       sid,
                    "score":            result["score"],
                    "recommendations":  result["recommendations"],
                    "evaluated_at":     timestamp
                },
                "session_id": sid
            }), 200

    # 4) Otherwise: ask next question (with constraints)
    lvl   = HRLevel.query.get(session.hr_level_id)
    first_q = (len(asked) == 0)
    sys_p = build_system_prompt(lvl, session.job_type, asked, first_question_only=first_q)

    msgs = [{"role":"system","content":sys_p}]
    for m in history:
        msgs.append({
            "role": "user" if m.sender=='user' else "model",
            "content": m.message
        })

    out   = generate_response(msgs)
    clean = strip_json(out)
    question = json.loads(clean)

    # If Gemini itself says "type":"end" here (e.g. on Q1 fails), handle it
    if question.get("type") == "end":
        eval_id   = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        rec = ChatEvaluation(
            id               = eval_id,
            session_id       = sid,
            score            = question["score"],
            recommendations  = json.dumps(question["recommendations"]),
            evaluated_at     = timestamp
        )
        db.session.add(rec)
        db.session.commit()

        return jsonify({
            "evaluation": {
                "id":               eval_id,
                "session_id":       sid,
                "score":            question["score"],
                "recommendations":  question["recommendations"],
                "evaluated_at":     timestamp
            },
            "session_id": sid
        }), 200

    # Normal question flow
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
    # 1) fetch all sessions for this user
    sessions = (
        ChatSession
        .query
        .filter_by(user_id=user_id)
        .order_by(ChatSession.started_at.desc())
        .all()
    )

    chats = []
    for s in sessions:
        # 2) get the latest message in the session
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
                    # strip any ``` fences and parse JSON
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
    if not User.query.get(user_id):
        return jsonify({'error':'User not found'}), 404
    if not Course.query.get(course_id):
        return jsonify({'error':'Course not found'}), 404

    enroll = enroll_course(user_id, course_id)
    payload = enroll.to_dict()
    # use 201 when first-time, 200 on re-activate
    status_code = 201 if enroll.enrolled_at == enroll.enrolled_at and enroll.enrolled_status and enroll.id else 200
    return jsonify(payload), status_code

# Unenroll from a Course
@app.route('/api/v1/feature/courses/unenroll', methods=['POST'])
def api_unenroll_course():
    data      = request.get_json() or {}
    user_id   = data.get('user_id')
    course_id = data.get('course_id')
    if not user_id or not course_id:
        return jsonify({'error':'user_id & course_id required'}), 400
    if not CourseEnrollment.query.filter_by(user_id=user_id, course_id=course_id).first():
        return jsonify({'error':'Enrollment not found'}), 404

    success = unenroll_course(user_id, course_id)
    # build a consistent payload
    course   = Course.query.get(course_id)
    payload  = {
        'user_id':        user_id,
        'course_id':      course_id,
        'enrolled_status': False,
        'course_title':   course.title,
        'provider':       course.provider,
    }
    return jsonify(payload), 200


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

# ---- User-Facing Roadmap Endpoints ----

# 1. List all available roadmaps
@app.route('/api/v1/roadmaps', methods=['GET'])
def list_roadmaps():
    rms = Roadmap.query.order_by(Roadmap.job_type, Roadmap.title).all()
    return jsonify([r.to_dict() for r in rms]), 200

# 2. Get roadmap details and its steps
@app.route('/api/v1/roadmaps/<string:roadmap_id>', methods=['GET'])
def get_roadmap(roadmap_id):
    rm = Roadmap.query.get(roadmap_id) or abort(404, 'Roadmap not found')
    return jsonify(rm.to_dict()), 200

# 3. User selects (starts) a roadmap
@app.route('/api/v1/users/<string:user_id>/roadmaps/<string:roadmap_id>/start', methods=['POST'])
def start_roadmap(user_id, roadmap_id):
    User.query.get(user_id)  or abort(404, 'User not found')
    Roadmap.query.get(roadmap_id) or abort(404, 'Roadmap not found')
    existing = UserRoadmap.query.filter_by(user_id=user_id, roadmap_id=roadmap_id).first()
    if existing:
        return jsonify({'message': 'Already started'}), 200

    ur = UserRoadmap(
        id=str(uuid.uuid4()),
        user_id=user_id,
        roadmap_id=roadmap_id,
        started_at=datetime.utcnow()
    )
    db.session.add(ur)
    db.session.commit()
    return jsonify(ur.to_dict()), 201

# 4. List user-selected roadmaps
@app.route('/api/v1/users/<string:user_id>/roadmaps', methods=['GET'])
def user_list_roadmaps(user_id):
    User.query.get(user_id) or abort(404, 'User not found')
    sels = UserRoadmap.query.filter_by(user_id=user_id).all()
    out = []
    for ur in sels:
        rm = Roadmap.query.get(ur.roadmap_id)
        out.append({
            **ur.to_dict(),
            'roadmap': {
                'id': rm.id,
                'job_type': rm.job_type,
                'title': rm.title,
                'description': rm.description
            }
        })
    return jsonify(out), 200

# 5. User unselects (removes) a roadmap
@app.route('/api/v1/users/<string:user_id>/roadmaps/<string:roadmap_id>', methods=['DELETE'])
def delete_user_roadmap(user_id, roadmap_id):
    ur = UserRoadmap.query.filter_by(user_id=user_id, roadmap_id=roadmap_id).first()
    if not ur:
        abort(404, 'Selection not found')

    # remove all progress tied to this selection
    UserRoadmapProgress.query.filter_by(user_roadmap_id=ur.id).delete(synchronize_session=False)
    # remove any achievement
    Achievement.query.filter_by(user_id=user_id, roadmap_id=roadmap_id).delete(synchronize_session=False)
    db.session.delete(ur)
    db.session.commit()
    return '', 204

# 6. User views progress
@app.route('/api/v1/users/<string:user_id>/roadmaps/<string:roadmap_id>/progress', methods=['GET'])
def user_progress(user_id, roadmap_id):
    User.query.get(user_id) or abort(404, 'User not found')
    Roadmap.query.get(roadmap_id) or abort(404, 'Roadmap not found')
    ur = UserRoadmap.query.filter_by(user_id=user_id, roadmap_id=roadmap_id).first()
    if not ur:
        abort(400, 'Roadmap not started')

    steps = RoadmapStep.query.filter_by(roadmap_id=roadmap_id)\
                             .order_by(RoadmapStep.step_order).all()
    result = []
    for s in steps:
        p = UserRoadmapProgress.query.filter_by(
            user_roadmap_id=ur.id, step_id=s.id
        ).first()
        result.append({
            **s.to_dict(),
            'completed':    bool(p),
            'completed_at': p.completed_at.isoformat() if p else None
        })
    return jsonify(result), 200

# 7. User completes a step
@app.route('/api/v1/users/<string:user_id>/roadmaps/<string:roadmap_id>/steps/<string:step_id>/complete', methods=['POST'])
def complete_step(user_id, roadmap_id, step_id):
    User.query.get(user_id)      or abort(404, 'User not found')
    rm = Roadmap.query.get(roadmap_id) or abort(404, 'Roadmap not found')
    step = RoadmapStep.query.get(step_id) or abort(404, 'Step not found')
    if step.roadmap_id != roadmap_id:
        abort(400, 'Step does not belong to this roadmap')

    ur = UserRoadmap.query.filter_by(user_id=user_id, roadmap_id=roadmap_id).first()
    if not ur:
        abort(400, 'Roadmap not started')

    exists = UserRoadmapProgress.query.filter_by(
        user_roadmap_id=ur.id, step_id=step_id
    ).first()
    if exists:
        return jsonify({'message': 'Step already completed'}), 200

    prog = UserRoadmapProgress(
        id=str(uuid.uuid4()),
        user_roadmap_id=ur.id,
        step_id=step_id,
        completed_at=datetime.utcnow()
    )
    db.session.add(prog)
    db.session.commit()

    # award achievement if done
    total = RoadmapStep.query.filter_by(roadmap_id=roadmap_id).count()
    done  = UserRoadmapProgress.query.filter_by(user_roadmap_id=ur.id).count()
    if done == total:
        ach = Achievement.query.filter_by(user_id=user_id, roadmap_id=roadmap_id).first()
        if not ach:
            ach = Achievement(
                id=str(uuid.uuid4()),
                user_id=user_id,
                roadmap_id=roadmap_id,
                earned_at=datetime.utcnow()
            )
            db.session.add(ach)
            db.session.commit()

    return jsonify({'step_id': step_id, 'completed_at': prog.completed_at.isoformat()}), 200

# 8. List user achievements
@app.route('/api/v1/users/<string:user_id>/achievements', methods=['GET'])
def list_achievements(user_id):
    User.query.get(user_id) or abort(404, 'User not found')
    achs = Achievement.query.filter_by(user_id=user_id).all()
    out = []
    for a in achs:
        rm = Roadmap.query.get(a.roadmap_id)
        out.append({
            **a.to_dict(),
            'roadmap': {
                'id':          rm.id,
                'job_type':    rm.job_type,
                'title':       rm.title,
                'description': rm.description
            }
        })
    return jsonify(out), 200

# -------------------- Mentorship Endpoints --------------------

# 1. Register as mentor
@app.route('/api/v1/mentorship/register', methods=['POST'])
def register_mentor():
    data = request.get_json() or {}
    user = User.query.get(data.get('user_id')) or abort(404, 'User not found')
    if getattr(user, 'is_mentor', False):
        return jsonify({'error': 'Already a mentor'}), 400

    profile = MentorProfile(
        id=str(uuid.uuid4()),
        user_id=user.id,
        expertise=data.get('expertise', ''),
        bio=data.get('bio', '')
    )
    user.is_mentor = True

    db.session.add(profile)
    db.session.commit()

    return jsonify(profile.to_dict()), 201


# 2. Search/List mentors (including mentor name)
@app.route('/api/v1/mentorship/mentors', methods=['GET'])
def list_mentors():
    q = request.args.get('q', '')
    mentors = MentorProfile.query \
        .filter(MentorProfile.expertise.ilike(f'%{q}%')) \
        .all()

    output = []
    for m in mentors:
        user = User.query.get(m.user_id)
        mp = m.to_dict()
        mp['name'] = user.name if user else None
        output.append(mp)

    return jsonify(output), 200


# 3. Set availability for a mentor
@app.route('/api/v1/mentorship/mentors/<mentor_id>/availability', methods=['POST'])
def set_availability(mentor_id):
    mentor = MentorProfile.query.get(mentor_id) or abort(404, 'Mentor not found')
    data = request.get_json() or {}
    avail = MentorAvailability(
        id=str(uuid.uuid4()),
        mentor_id=mentor.id,
        start_datetime=datetime.fromisoformat(data['start_datetime']),
        end_datetime=datetime.fromisoformat(data['end_datetime'])
    )
    db.session.add(avail)
    db.session.commit()
    return jsonify(avail.to_dict()), 201


# 4. Get availability for a mentor
@app.route('/api/v1/mentorship/mentors/<mentor_id>/availability', methods=['GET'])
def get_availability(mentor_id):
    MentorProfile.query.get_or_404(mentor_id, description='Mentor not found')
    avails = MentorAvailability.query.filter_by(mentor_id=mentor_id).all()
    return jsonify([a.to_dict() for a in avails]), 200


# 5. Book a mentoring session
@app.route('/api/v1/mentorship/sessions', methods=['POST'])
def book_session():
    data = request.get_json() or {}
    avail = MentorAvailability.query.get(data.get('availability_id')) or abort(404, 'Availability slot not found')

    # generate dummy Google Meet link
    link_code = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10))
    meet_link = f"https://meet.google.com/{link_code}"

    sess = MentorshipSession(
        id=str(uuid.uuid4()),
        mentee_id=data.get('mentee_id'),
        mentor_id=avail.mentor_id,
        scheduled_at=avail.start_datetime,
        meet_link=meet_link
    )
    # remove availability slot once booked
    db.session.add(sess)
    db.session.delete(avail)
    db.session.commit()

    return jsonify(sess.to_dict()), 201


# 6. Submit feedback after session
@app.route('/api/v1/mentorship/sessions/<session_id>/feedback', methods=['POST'])
def submit_feedback(session_id):
    sess = MentorshipSession.query.get(session_id) or abort(404, 'Session not found')
    if getattr(sess, 'feedback', None):
        return jsonify({'error': 'Feedback already submitted'}), 400

    data = request.get_json() or {}
    fb = MentorshipFeedback(
        id=str(uuid.uuid4()),
        session_id=sess.id,
        rating=data.get('rating'),
        feedback=data.get('feedback', '')
    )
    sess.completed = True

    db.session.add(fb)
    db.session.commit()

    return jsonify(fb.to_dict()), 201


# 7. Get a single mentor’s full profile (with work experiences)
@app.route('/api/v1/mentorship/mentors/<mentor_id>/profile', methods=['GET'])
def get_mentor_profile(mentor_id):
    profile = MentorProfile.query.get(mentor_id) or abort(404, 'Mentor not found')
    user = User.query.get(profile.user_id) or abort(404, 'User not found')

    exps = WorkExperience.query \
        .filter_by(user_id=profile.user_id) \
        .order_by(WorkExperience.start_year.desc(), WorkExperience.start_month.desc()) \
        .all()

    work_list = []
    for e in exps:
        work_list.append({
            'id':           e.id,
            'job_title':    e.job_title,
            'company_name': e.company_name,
            'job_desc':     e.job_desc,
            'start_month':  e.start_month,
            'start_year':   e.start_year,
            'end_month':    e.end_month,
            'end_year':     e.end_year,
            'is_current':   bool(e.is_current),
        })

    resp = {
        'mentor_profile': {
            'id':         profile.id,
            'user_id':    profile.user_id,
            'name':       user.name,
            'expertise':  profile.expertise,
            'bio':        profile.bio,
            'created_at': profile.created_at.isoformat()
        },
        'work_experiences': work_list
    }
    return jsonify(resp), 200


if __name__ == '__main__':
    app.run(debug=True)