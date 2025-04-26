# core/courses.py
from core.db import db
from core.models import Course

def list_courses():
    return Course.query.order_by(Course.created_at.desc()).all()

def get_course(course_id):
    return Course.query.get(course_id)
