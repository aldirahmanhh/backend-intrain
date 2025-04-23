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

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Import models after db initialization
from core.models import (
    User, HRLevel,
    ChatSession, ChatMessage,
    CVSubmission, CVReview, CVReviewSection, Course, Job
)

# Remove in-memory storage
# users = {}
# conversation_context = {}

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from server import db

# Model untuk level HR
class HRLevel(db.Model):
    __tablename__ = 'hr_levels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(100))
    difficulty_rank = db.Column(db.SmallInteger, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'difficulty_rank': self.difficulty_rank
        }

# Model User
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

# Model ChatSession
class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    hr_level_id = db.Column(db.Integer, db.ForeignKey('hr_levels.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'hr_level_id': self.hr_level_id,
            'started_at': self.started_at.isoformat()
        }

# Model ChatMessage
class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    session_id = db.Column(db.String(36), db.ForeignKey('chat_sessions.id'), nullable=False)
    sender = db.Column(db.Enum('user', 'bot', name='sender_enum'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'sender': self.sender,
            'message': self.message,
            'sent_at': self.sent_at.isoformat()
        }

# Model CVSubmission
class CVSubmission(db.Model):
    __tablename__ = 'cv_submissions'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.Enum('pdf', 'jpg', 'jpeg', 'png', name='file_type_enum'), nullable=False)
    file_url = db.Column(db.String(500), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'file_name': self.file_name,
            'file_type': self.file_type,
            'file_url': self.file_url,
            'uploaded_at': self.uploaded_at.isoformat()
        }

# Model CVReview
class CVReview(db.Model):
    __tablename__ = 'cv_reviews'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id = db.Column(db.String(36), db.ForeignKey('cv_submissions.id'), nullable=False)
    reviewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    ats_passed = db.Column(db.Boolean, nullable=False)
    overall_feedback = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'submission_id': self.submission_id,
            'reviewed_at': self.reviewed_at.isoformat(),
            'ats_passed': self.ats_passed,
            'overall_feedback': self.overall_feedback
        }

# Model CVReviewSection
class CVReviewSection(db.Model):
    __tablename__ = 'cv_review_sections'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    review_id = db.Column(db.String(36), db.ForeignKey('cv_reviews.id'), nullable=False)
    section = db.Column(db.Enum(
        'profile_summary', 'education', 'experience',
        'skills', 'certification', 'portfolio',
        name='cv_sections_enum'
    ), nullable=False)
    needs_improvement = db.Column(db.Boolean, nullable=False)
    feedback = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'review_id': self.review_id,
            'section': self.section,
            'needs_improvement': self.needs_improvement,
            'feedback': self.feedback
        }

# Model Course
class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    provider = db.Column(db.String(100))
    url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'provider': self.provider,
            'url': self.url,
            'created_at': self.created_at.isoformat()
        }

# Model Job
class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(100))
    location = db.Column(db.String(100))
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'description': self.description,
            'requirements': self.requirements,
            'posted_at': self.posted_at.isoformat()
        }
