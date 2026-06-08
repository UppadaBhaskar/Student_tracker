"""Seed trainer account and optional demo data."""
import os
from datetime import date, timedelta

from sqlalchemy import select

from app import create_app
from app.extensions import db
from app.models import (
    Assignment,
    Attendance,
    DailyNote,
    Question,
    Student,
    Subject,
    User,
    WorkshopEntity,
)
from app.models.enums import (
    AssignmentStatus,
    AttendanceStatus,
    EntityType,
    QuestionDifficulty,
    QuestionStatus,
    UserRole,
)
from app.services.auth_service import AuthService


def seed():
    app = create_app()
    with app.app_context():
        auth = AuthService()
        trainer_email = app.config["TRAINER_EMAIL"]
        if not db.session.scalar(select(User).where(User.email == trainer_email)):
            auth.create_user(trainer_email, app.config["TRAINER_PASSWORD"], UserRole.TRAINER)
            db.session.commit()
            print(f"Created trainer: {trainer_email}")
        else:
            print(f"Trainer already exists: {trainer_email}")

        if not app.config.get("SEED_DEMO_DATA"):
            print("SEED_DEMO_DATA=false — skipping demo workshop data.")
            return

        if db.session.scalar(select(WorkshopEntity).limit(1)):
            print("Demo data already exists, skipping.")
            return

        start = date.today()
        entity = WorkshopEntity(
            name="Python Workshop 2026",
            entity_type=EntityType.WORKSHOP,
            total_days=15,
            start_date=start,
            end_date=start + timedelta(days=14),
        )
        db.session.add(entity)
        db.session.flush()

        python = Subject(entity_id=entity.id, name="Python")
        sql = Subject(entity_id=entity.id, name="SQL")
        db.session.add_all([python, sql])
        db.session.flush()

        demo_students = [
            ("USN001", "Alice Kumar", "alice@demo.local", "student123"),
            ("USN002", "Bob Sharma", "bob@demo.local", "student123"),
            ("USN003", "Carol Reddy", "carol@demo.local", "student123"),
            ("USN004", "David Nair", "david@demo.local", "student123"),
            ("USN005", "Eva Thomas", "eva@demo.local", "student123"),
        ]
        for usn, name, email, password in demo_students:
            user = auth.create_user(email, password, UserRole.STUDENT)
            db.session.flush()
            db.session.add(
                Student(
                    user_id=user.id,
                    entity_id=entity.id,
                    usn=usn,
                    full_name=name,
                    college="Demo College",
                    branch="CSE",
                )
            )
        db.session.flush()

        students = db.session.scalars(select(Student).where(Student.entity_id == entity.id)).all()
        for student in students:
            db.session.add(
                Attendance(
                    entity_id=entity.id,
                    student_id=student.id,
                    day=1,
                    status=AttendanceStatus.PRESENT,
                )
            )
            db.session.add(
                Assignment(
                    entity_id=entity.id,
                    student_id=student.id,
                    day=1,
                    status=AssignmentStatus.COMPLETED,
                )
            )

        db.session.add(
            Question(
                entity_id=entity.id,
                question_number=1,
                subject_id=python.id,
                title="Reverse String",
                description="Write a function to reverse a string.",
                day=1,
                timer_minutes=30,
                difficulty=QuestionDifficulty.MEDIUM,
                max_points=10,
                status=QuestionStatus.DRAFT,
            )
        )

        db.session.add(
            DailyNote(
                entity_id=entity.id,
                day=1,
                notes="Introduction to Python basics. Good participation.",
            )
        )

        db.session.commit()
        print("Demo entity, subjects, students, and sample data created.")


if __name__ == "__main__":
    seed()
