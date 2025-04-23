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

db = SQLAlchemy(app)

# Import models after initializing db
from core.models import (
    User, HRLevel,
    ChatSession, ChatMessage,
    CVSubmission, CVReview, CVReviewSection,
    Course, Job
)

@app.route('/')
def index():
    return "Server is Online!"

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

# Helper: serialize SQLAlchemy objects
def serialize(obj):
    return obj.to_dict() if hasattr(obj, 'to_dict') else {}

# Chat Endpoint
def get_or_create_session(user_id):
    session = (
        ChatSession.query
        .filter_by(user_id=user_id)
        .order_by(ChatSession.started_at.desc())
        .first()
    )
    if not session:
        # default to easiest level
        easy_level = HRLevel.query.filter_by(difficulty_rank=1).first()
        session = ChatSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            hr_level_id=easy_level.id if easy_level else 1
        )
        db.session.add(session)
        db.session.commit()
    return session

@app.route('/api/v1/feature/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    user_msg = data.get('message')
    if not user_id or not user_msg:
        return jsonify({'error': 'Parameters user_id and message are required.'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found. Please register first.'}), 404

    session = get_or_create_session(user_id)

    # Save user message
    user_msg_obj = ChatMessage(
        session_id=session.id,
        sender='user',
        message=user_msg
    )
    db.session.add(user_msg_obj)
    db.session.commit()

    # Build context for Gemini
    msgs = ChatMessage.query.filter_by(session_id=session.id).order_by(ChatMessage.sent_at).all()
    contents = [
        types.Content(role=m.sender, parts=[types.Part.from_text(text=m.message)])
        for m in msgs
    ]

    try:
        reply_text = generate_response(contents)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Save bot reply
    bot_msg_obj = ChatMessage(
        session_id=session.id,
        sender='bot',
        message=reply_text
    )
    db.session.add(bot_msg_obj)
    db.session.commit()

    return jsonify({
        'response': reply_text,
        'session': serialize(session)
    }), 200

# User Register
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
        password_hash=password,
        name=data.get('name', ''),
        email=data.get('email', '')
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Registration successful.', 'user': serialize(user)}), 201

# User Login
@app.route('/api/v1/auth/user/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Parameters username and password are required.'}), 400

    user = User.query.filter_by(username=username, password_hash=password).first()
    if not user:
        return jsonify({'error': 'Incorrect username or password.'}), 401

    return jsonify({'message': 'Login successful.', 'user': serialize(user)}), 200

# Update User
@app.route('/api/v1/auth/user/update', methods=['PUT'])
def update_user():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'Parameter user_id is required.'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found.'}), 404

    # Updatable fields
    for field in ['username', 'password_hash', 'name', 'email']:
        if field in data:
            setattr(user, field, data[field])
    db.session.commit()

    return jsonify({'message': 'User data updated successfully.', 'user': serialize(user)}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
