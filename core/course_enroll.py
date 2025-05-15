# core/course_enroll.py
import uuid
from datetime import datetime
from core.db import db
from core.models import CourseEnrollment

def enroll_course(user_id: str, course_id: str) -> CourseEnrollment:
    """
    Soft-enroll a user in a course. Returns the enrollment.
    """
    enroll = CourseEnrollment.query.filter_by(
        user_id=user_id, course_id=course_id
    ).first()

    if enroll:
        # if it existed but was “unenrolled”, re-activate it
        if not enroll.enrolled_status:
            enroll.enrolled_status = True
            enroll.enrolled_at     = datetime.utcnow()
            db.session.commit()
        return enroll

    # first-time enroll
    enroll = CourseEnrollment(
        id=str(uuid.uuid4()),
        user_id=user_id,
        course_id=course_id,
        enrolled_status=True
    )
    db.session.add(enroll)
    db.session.commit()
    return enroll

def unenroll_course(user_id: str, course_id: str) -> bool:
    """
    Soft-unenroll a user. Returns True if record existed.
    """
    enroll = CourseEnrollment.query.filter_by(
        user_id=user_id, course_id=course_id
    ).first()
    if not enroll:
        return False

    enroll.enrolled_status = False
    db.session.commit()
    return True

def complete_course(user_id: str, course_id: str) -> CourseEnrollment:
    """
    Mark an existing enrollment as completed.
    Returns the updated enrollment or None if not enrolled.
    """
    enroll = CourseEnrollment.query.filter_by(
        user_id=user_id, course_id=course_id
    ).first()
    if not enroll:
        return None
    if not enroll.is_completed:
        enroll.is_completed  = True
        enroll.completed_at  = datetime.utcnow()
        db.session.commit()
    return enroll

def list_user_enrollments(user_id: str) -> list[CourseEnrollment]:
    """
    List all enrollments for a user.
    """
    return CourseEnrollment.query.filter_by(user_id=user_id).all()
