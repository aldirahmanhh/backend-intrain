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

# Retrieve or start a chat session for a user
def get_or_create_session(user_id):
    session = (
        ChatSession.query
        .filter_by(user_id=user_id)
        .order_by(ChatSession.started_at.desc())
        .first()
    )
    if not session:
        easy = HRLevel.query.filter_by(difficulty_rank=1).first()
        session = ChatSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            hr_level_id=easy.id if easy else 1
        )
        db.session.add(session)
        db.session.commit()
    return session

@app.route('/')
def index():
    return "Server is Online!"

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

@app.route('/api/v1/feature/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    message = data.get('message')
    if not user_id or not message:
        return jsonify({'error': 'Parameters user_id and message are required.'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found. Please register first.'}), 404

    sess = get_or_create_session(user_id)

    # save user message
    db.session.add(ChatMessage(
        session_id=sess.id,
        sender='user',
        message=message
    ))
    db.session.commit()

    # build context
    history = (ChatMessage.query
               .filter_by(session_id=sess.id)
               .order_by(ChatMessage.sent_at)
               .all())
    contents = [
        types.Content(role=m.sender, parts=[types.Part.from_text(text=m.message)])
        for m in history
    ]

    try:
        reply = generate_response(contents)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # save bot reply
    db.session.add(ChatMessage(
        session_id=sess.id,
        sender='bot',
        message=reply
    ))
    db.session.commit()

    return jsonify({
        'response': reply,
        'session': serialize(sess)
    }), 200

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

if __name__ == '__main__':
    app.run(debug=True)
