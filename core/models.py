# core/models.py
import uuid
import json
from datetime import datetime
from core.db import db
from werkzeug.security import generate_password_hash, check_password_hash

class HRLevel(db.Model):
    __tablename__ = 'hr_levels'
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(20), nullable=False)
    description     = db.Column(db.String(100))
    difficulty_rank = db.Column(db.SmallInteger, nullable=False)

    def to_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            description=self.description,
            difficulty_rank=self.difficulty_rank
        )

class User(db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username      = db.Column(db.String(50), unique=True, nullable=False)
    password      = db.Column(db.String(255), nullable=False)
    name          = db.Column(db.String(100))
    email         = db.Column(db.String(100), unique=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    # ————— Mentorship fields & relasi —————
    is_mentor         = db.Column(db.Boolean, default=False, nullable=False)
    mentor_profile    = db.relationship('MentorProfile', uselist=False, back_populates='user', cascade='all, delete-orphan')
    mentee_sessions   = db.relationship('MentorshipSession', back_populates='mentee', cascade='all, delete-orphan')

    def set_password(self, raw_password):
        """Hash & store the password."""
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password) -> bool:
        """Return True if raw_password matches the stored hash."""
        return check_password_hash(self.password, raw_password)

    def to_dict(self):
        # don’t include password!
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'is_mentor': self.is_mentor
        }
    
class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    id              = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id         = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    hr_level_id     = db.Column(db.Integer, db.ForeignKey('hr_levels.id'), nullable=False)
    job_type        = db.Column(db.String(200), nullable=False); total_questions = db.Column(db.Integer, nullable=False, default=0)
    started_at      = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self):
        return dict(
            id=self.id,
            user_id=self.user_id,
            hr_level_id=self.hr_level_id,
            job_type=self.job_type,
            total_questions=self.total_questions,
            started_at=self.started_at.isoformat()
        )
class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id          = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id  = db.Column(db.String(36), db.ForeignKey('chat_sessions.id'), nullable=False)
    sender      = db.Column(db.Enum('user','bot', name='sender_enum'), nullable=False)
    message     = db.Column(db.Text, nullable=False)
    sent_at     = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return dict(
            id=self.id,
            session_id=self.session_id,
            sender=self.sender,
            message=self.message,
            sent_at=self.sent_at.isoformat()
        )
    
class ChatEvaluation(db.Model):
    __tablename__ = 'chat_evaluations'
    id              = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id      = db.Column(db.String(36), db.ForeignKey('chat_sessions.id'), nullable=False)
    score           = db.Column(db.SmallInteger, nullable=False)
    recommendations = db.Column(db.Text, nullable=False)  # store JSON list as text
    evaluated_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return dict(
            id=self.id,
            session_id=self.session_id,
            score=self.score,
            recommendations=json.loads(self.recommendations),
            evaluated_at=self.evaluated_at.isoformat()
        )

class CVSubmission(db.Model):
    __tablename__ = 'cv_submissions'
    id            = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id       = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    file_name     = db.Column(db.String(255), nullable=False)
    file_type     = db.Column(db.Enum('pdf','jpg','jpeg','png', name='file_type_enum'), nullable=False)
    file_url      = db.Column(db.String(500), nullable=False)
    uploaded_at   = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return dict(
            id=self.id,
            user_id=self.user_id,
            file_name=self.file_name,
            file_type=self.file_type,
            file_url=self.file_url,
            uploaded_at=self.uploaded_at.isoformat()
        )

class CVReview(db.Model):
    __tablename__ = 'cv_reviews'
    id              = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id   = db.Column(db.String(36), db.ForeignKey('cv_submissions.id'), nullable=False)
    reviewed_at     = db.Column(db.DateTime, default=datetime.utcnow)
    ats_passed      = db.Column(db.Boolean, nullable=False)
    overall_feedback= db.Column(db.Text)

    def to_dict(self):
        return dict(
            id=self.id,
            submission_id=self.submission_id,
            reviewed_at=self.reviewed_at.isoformat(),
            ats_passed=self.ats_passed,
            overall_feedback=self.overall_feedback
        )

class CVReviewSection(db.Model):
    __tablename__ = 'cv_review_sections'
    id                = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    review_id         = db.Column(db.String(36), db.ForeignKey('cv_reviews.id'), nullable=False)
    section           = db.Column(db.Enum(
                            'profile_summary','education','experience',
                            'skills','certification','portfolio',
                            name='cv_sections_enum'
                        ), nullable=False)
    needs_improvement = db.Column(db.Boolean, nullable=False)
    feedback          = db.Column(db.Text)

    def to_dict(self):
        return dict(
            id=self.id,
            review_id=self.review_id,
            section=self.section,
            needs_improvement=self.needs_improvement,
            feedback=self.feedback
        )

class Course(db.Model):
    __tablename__ = 'courses'
    id          = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title       = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    provider    = db.Column(db.String(100))
    url         = db.Column(db.String(500))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return dict(
            id=self.id,
            title=self.title,
            description=self.description,
            provider=self.provider,
            url=self.url,
            created_at=self.created_at.isoformat()
        )

class CourseEnrollment(db.Model):
    __tablename__ = 'course_enrollments'

    id              = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id         = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    course_id       = db.Column(db.String(36), db.ForeignKey('courses.id'), nullable=False)
    enrolled_at     = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_completed    = db.Column(db.Boolean, default=False, nullable=False)
    completed_at    = db.Column(db.DateTime)
    enrolled_status = db.Column(db.Boolean, default=False, nullable=False)

    # <-- add this:
    course = db.relationship('Course', backref='enrollments')

    def to_dict(self):
        return {
            'id':               self.id,
            'user_id':          self.user_id,
            'course_id':        self.course_id,
            'enrolled_at':      self.enrolled_at.isoformat(),
            'is_completed':     self.is_completed,
            'completed_at':     self.completed_at.isoformat() if self.completed_at else None,
            'enrolled_status':  self.enrolled_status,
            'course_title':     self.course.title,
            'provider':         self.course.provider,
        }

    
class Job(db.Model):
    __tablename__ = 'jobs'
    id           = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title        = db.Column(db.String(200), nullable=False)
    company      = db.Column(db.String(100))
    location     = db.Column(db.String(100))
    description  = db.Column(db.Text)
    requirements = db.Column(db.Text)
    posted_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return dict(
            id=self.id,
            title=self.title,
            company=self.company,
            location=self.location,
            description=self.description,
            requirements=self.requirements,
            posted_at=self.posted_at.isoformat()
        )
    
class WorkExperience(db.Model):
    __tablename__ = 'work_experiences'
    id            = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id       = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    job_title     = db.Column(db.String(200), nullable=False)
    company_name  = db.Column(db.String(200), nullable=False)
    job_desc      = db.Column(db.Text)
    start_month   = db.Column(db.SmallInteger, nullable=False)
    start_year    = db.Column(db.SmallInteger, nullable=False)
    end_month     = db.Column(db.SmallInteger)
    end_year      = db.Column(db.SmallInteger)
    is_current    = db.Column(db.Boolean, default=False, nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return dict(
            id=self.id,
            user_id=self.user_id,
            job_title=self.job_title,
            company_name=self.company_name,
            job_desc=self.job_desc,
            start_month=self.start_month,
            start_year=self.start_year,
            end_month=self.end_month,
            end_year=self.end_year,
            is_current=self.is_current,
            created_at=self.created_at.isoformat()
        )

class Roadmap(db.Model):
    __tablename__ = 'roadmaps'
    id          = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_type    = db.Column(db.String(200), nullable=False)
    title       = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    steps = db.relationship(
        'RoadmapStep',
        backref='roadmap',
        cascade='all, delete-orphan',
        order_by='RoadmapStep.step_order'
    )

    def to_dict(self):
        return {
            'id':          self.id,
            'job_type':    self.job_type,
            'title':       self.title,
            'description': self.description,
            'steps':       [s.to_dict() for s in self.steps]
        }

class RoadmapStep(db.Model):
    __tablename__ = 'roadmap_steps'
    id          = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    roadmap_id  = db.Column(db.String(36), db.ForeignKey('roadmaps.id'), nullable=False)
    step_order  = db.Column(db.Integer, nullable=False)
    title       = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    course_id   = db.Column(db.String(36), db.ForeignKey('courses.id'))

    def to_dict(self):
        return {
            'id':          self.id,
            'step_order':  self.step_order,
            'title':       self.title,
            'description': self.description,
            'course_id':   self.course_id
        }

class UserRoadmap(db.Model):
    __tablename__ = 'user_roadmaps'
    id          = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id     = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    roadmap_id  = db.Column(db.String(36), db.ForeignKey('roadmaps.id'), nullable=False)
    started_at  = db.Column(db.DateTime, default=datetime.utcnow)

    progress = db.relationship(
        'UserRoadmapProgress',
        backref='user_roadmap',
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            'id':         self.id,
            'user_id':    self.user_id,
            'roadmap_id': self.roadmap_id,
            'started_at': self.started_at.isoformat()
        }

class UserRoadmapProgress(db.Model):
    __tablename__ = 'user_roadmap_progress'
    id               = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_roadmap_id  = db.Column(db.String(36), db.ForeignKey('user_roadmaps.id'), nullable=False)
    step_id          = db.Column(db.String(36), db.ForeignKey('roadmap_steps.id'), nullable=False)
    completed_at     = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':              self.id,
            'user_roadmap_id': self.user_roadmap_id,
            'step_id':         self.step_id,
            'completed_at':    self.completed_at.isoformat()
        }

class Achievement(db.Model):
    __tablename__ = 'achievements'
    id          = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id     = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    roadmap_id  = db.Column(db.String(36), db.ForeignKey('roadmaps.id'), nullable=False)
    earned_at   = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':         self.id,
            'user_id':    self.user_id,
            'roadmap_id': self.roadmap_id,
            'earned_at':  self.earned_at.isoformat()
        }

class MentorProfile(db.Model):
    __tablename__ = 'mentor_profiles'
    id           = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id      = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)
    expertise    = db.Column(db.String(200), nullable=False)
    bio          = db.Column(db.Text)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    user         = db.relationship('User', back_populates='mentor_profile')
    availabilities = db.relationship('MentorAvailability', back_populates='mentor', cascade='all, delete-orphan')
    sessions       = db.relationship('MentorshipSession', back_populates='mentor', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id':         self.id,
            'user_id':    self.user_id,
            'expertise':  self.expertise,
            'bio':        self.bio,
            'created_at': self.created_at.isoformat()
        }

class MentorAvailability(db.Model):
    __tablename__ = 'mentor_availabilities'
    id             = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    mentor_id      = db.Column(db.String(36), db.ForeignKey('mentor_profiles.id'), nullable=False)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime   = db.Column(db.DateTime, nullable=False)

    mentor         = db.relationship('MentorProfile', back_populates='availabilities')

    def to_dict(self):
        return {
            'id':             self.id,
            'mentor_id':      self.mentor_id,
            'start_datetime': self.start_datetime.isoformat(),
            'end_datetime':   self.end_datetime.isoformat()
        }

class MentorshipSession(db.Model):
    __tablename__ = 'mentorship_sessions'
    id            = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    mentee_id     = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    mentor_id     = db.Column(db.String(36), db.ForeignKey('mentor_profiles.id'), nullable=False)
    scheduled_at  = db.Column(db.DateTime, nullable=False)
    meet_link     = db.Column(db.String(300), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    completed     = db.Column(db.Boolean, default=False, nullable=False)

    mentee        = db.relationship('User', back_populates='mentee_sessions')
    mentor        = db.relationship('MentorProfile', back_populates='sessions')
    feedback      = db.relationship('MentorshipFeedback', back_populates='session', uselist=False, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id':            self.id,
            'mentee_id':     self.mentee_id,
            'mentor_id':     self.mentor_id,
            'scheduled_at':  self.scheduled_at.isoformat(),
            'meet_link':     self.meet_link,
            'created_at':    self.created_at.isoformat(),
            'completed':     self.completed
        }

class MentorshipFeedback(db.Model):
    __tablename__ = 'mentorship_feedback'
    id          = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id  = db.Column(db.String(36), db.ForeignKey('mentorship_sessions.id'), nullable=False)
    rating      = db.Column(db.SmallInteger, nullable=False)  # 1–5
    feedback    = db.Column(db.Text)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    session     = db.relationship('MentorshipSession', back_populates='feedback')

    def to_dict(self):
        return {
            'id':          self.id,
            'session_id':  self.session_id,
            'rating':      self.rating,
            'feedback':    self.feedback,
            'created_at':  self.created_at.isoformat()
        }