import uuid
import os
import dotenv

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

from google import genai
from google.genai import types
from core.generate import generate_response

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
    Course, Job
)


# Create tables immediately to ensure schema is in place
with app.app_context():
    db.create_all()

# Utility to serialize SQLAlchemy models
def serialize(obj):
    return obj.to_dict() if hasattr(obj, 'to_dict') else {}

def map_role(sender):
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

    return jsonify({'message': 'Registration successful.', 'user': serialize(user)}), 201

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

    return jsonify({'message': 'User data updated successfully.', 'user': serialize(user)}), 200


# HR Chatbot API Endpoints
def build_system_prompt(hr_level, job_type):
    rank = hr_level.difficulty_rank
    if rank == 1:
        return (
            f"You are an HR interviewer conducting a relaxed, entry-level interview for the position of {job_type}. "
                "Your goal is to help the candidate feel comfortable and highlight their basic skills and personality. "
                "Ask 3 to 5 (one by one wait until the candidate answers the questions given tough questions) straightforward, friendly questions such as:\n"
                "1. “Can you tell me a little about yourself and why you’re interested in this role?”\n"
                "2. “What relevant experience or coursework do you have?”\n"
                "3. “How would you describe your strengths and areas for growth?”\n"
                "4. “Can you share an example of when you worked successfully in a team?”\n"
                "5. “What motivates you to perform well at work?”\n"
                "Keep your tone warm, supportive, and encouraging throughout the conversation."
        )
    elif rank == 2:
        return (
            f"You are an HR interviewer for the position of {job_type}, conducting a standard professional interview. "
                "Ask 5 to 7 (one by one wait until the candidate answers the questions given tough questions) balanced questions that probe both behavioral and technical competencies, for example:\n"
                "1. “Describe a challenging project you managed and how you overcame obstacles.”\n"
                "2. “How do you prioritize tasks when you have multiple deadlines?”\n"
                "3. “Tell me about a time you had to give constructive feedback to a colleague.”\n"
                "4. “What tools or methods do you use to ensure quality in your work?”\n"
                "5. “How do you stay current with developments in your field?”\n"
                "6. “Can you walk me through a specific achievement you’re proud of?”\n"
                "Maintain a respectful, neutral tone—professional but not intimidating."
        )
    else:
        return (
            f"You are an HR interviewer for the position of {job_type}. Assume a subtly sarcastic and challenging demeanor to create a tense atmosphere. "
                "Your aim is to test the candidate’s composure under pressure and make them work hard to impress you. Ask 7 to 10 (one by one wait until the candidate answers the questions given tough questions) such as:\n"
                "1. “So, what makes you think you’re even remotely qualified for this role?”\n"
                "2. “Explain a time you failed spectacularly—if you can call it failure.”\n"
                "3. “Why should we choose you over ten other candidates who might actually know what they’re doing?”\n"
                "4. “Walk me through a complex problem you solved. Don’t gloss over the details—make me work for it.”\n"
                "5. “What’s your biggest weakness? And no, ‘overly dedicated’ doesn’t count.”\n"
                "6. “How do you handle feedback—if you can handle it?”\n"
                "7. “Sell me on one skill you claim to have, but I’m skeptical about it.”\n"
                "Use ironic remarks and maintain a controlled, critical tone to keep the candidate on edge throughout the interview."
        )

@app.route('/api/v1/hr_levels', methods=['GET'])
def list_hr_levels():
    levels = HRLevel.query.order_by(HRLevel.difficulty_rank).all()
    return jsonify([l.to_dict() for l in levels]), 200

def map_role(sender):
    # Gemini expects 'user' or 'model'
    return 'user' if sender == 'user' else 'model'

def build_system_prompt(hr_level, job_type):
    rank = hr_level.difficulty_rank

@app.route('/api/v1/feature/interview/chat', methods=['POST'])
def chat():
    d      = request.get_json() or {}
    sid    = d.get('session_id')
    uid    = d.get('user_id')
    text   = d.get('message')
    hrid   = d.get('hr_level_id')
    job    = d.get('job_type')
    evalf  = d.get('evaluate', False)

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

if __name__ == '__main__':
    app.run(debug=True)
