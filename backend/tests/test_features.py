"""Integration tests for analytics, dashboard, leaderboard, risk, and Excel features."""
from datetime import date, timedelta

from app.extensions import db
from app.models import Assignment, Attendance, Question, Student, Subject, User, WorkshopEntity
from app.models.enums import (
    AssignmentStatus,
    AttendanceStatus,
    EntityType,
    QuestionDifficulty,
    QuestionStatus,
    UserRole,
)
from app.services.auth_service import AuthService
from app.services.risk_service import RiskService


def _seed_entity(app):
    with app.app_context():
        auth = AuthService()
        entity = WorkshopEntity(
            name="Test Workshop",
            entity_type=EntityType.WORKSHOP,
            total_days=5,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=4),
        )
        db.session.add(entity)
        db.session.flush()

        subject = Subject(entity_id=entity.id, name="Python")
        db.session.add(subject)
        db.session.flush()

        user = auth.create_user("alice@test.local", "student123", UserRole.STUDENT)
        db.session.flush()
        student = Student(
            user_id=user.id,
            entity_id=entity.id,
            usn="USN100",
            full_name="Alice Test",
            college="Test College",
            branch="CSE",
        )
        db.session.add(student)
        db.session.flush()

        db.session.add(
            Attendance(student_id=student.id, entity_id=entity.id, day=1, status=AttendanceStatus.PRESENT)
        )
        db.session.add(
            Assignment(
                student_id=student.id,
                entity_id=entity.id,
                day=1,
                status=AssignmentStatus.COMPLETED,
            )
        )
        db.session.add(
            Question(
                entity_id=entity.id,
                subject_id=subject.id,
                question_number=1,
                title="Hello World",
                description="Print hello",
                day=1,
                timer_minutes=30,
                difficulty=QuestionDifficulty.MEDIUM,
                max_points=10,
                status=QuestionStatus.DRAFT,
            )
        )
        db.session.commit()
        return entity.id, student.id


def test_health(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.get_json()["data"]["status"] == "ok"


def test_trainer_dashboard_and_analytics(client, trainer_headers, app):
    entity_id, _ = _seed_entity(app)

    dash = client.get(f"/api/v1/entities/{entity_id}/trainer-dashboard", headers=trainer_headers)
    assert dash.status_code == 200
    data = dash.get_json()["data"]
    assert data["today_summary"]["total_students"] == 1
    assert "risk_distribution" in data
    assert "at_risk_students" in data
    assert "attendance_trend" in data

    analytics = client.get(f"/api/v1/entities/{entity_id}/analytics", headers=trainer_headers)
    assert analytics.status_code == 200
    analytics_data = analytics.get_json()["data"]
    assert "attendance_trend" in analytics_data
    assert analytics_data["risk_distribution"]["green"] + analytics_data["risk_distribution"]["yellow"] + analytics_data["risk_distribution"]["red"] == 1


def test_leaderboard_and_risk(client, trainer_headers, app):
    entity_id, student_id = _seed_entity(app)

    board = client.get(f"/api/v1/entities/{entity_id}/leaderboard", headers=trainer_headers)
    assert board.status_code == 200
    entries = board.get_json()["data"]
    assert len(entries) == 1
    assert entries[0]["student_name"] == "Alice Test"
    assert "risk" in entries[0]

    at_risk = client.get(f"/api/v1/entities/{entity_id}/at-risk-students", headers=trainer_headers)
    assert at_risk.status_code == 200
    assert isinstance(at_risk.get_json()["data"], list)

    risk = RiskService().assess_student(student_id)
    assert risk["overall"] in ("green", "yellow", "red")
    assert "dimensions" in risk


def test_excel_export_and_template(client, trainer_headers, app):
    entity_id, _ = _seed_entity(app)

    for export_type in ("students", "leaderboard", "analytics-summary"):
        res = client.get(
            f"/api/v1/entities/{entity_id}/export/{export_type}",
            headers=trainer_headers,
        )
        assert res.status_code == 200
        assert len(res.data) > 0

    template = client.get("/api/v1/entities/import-templates/students", headers=trainer_headers)
    assert template.status_code == 200
    assert len(template.data) > 0


def test_student_leaderboard_scoped(client, trainer_headers, student_headers, app):
    entity_id, _ = _seed_entity(app)

    with app.app_context():
        auth = AuthService()
        other_entity = WorkshopEntity(
            name="Other Workshop",
            entity_type=EntityType.WORKSHOP,
            total_days=5,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=4),
        )
        db.session.add(other_entity)
        db.session.flush()
        student_user = db.session.scalar(
            __import__("sqlalchemy").select(User).where(User.email == "student@test.local")
        )
        db.session.add(
            Student(
                user_id=student_user.id,
                entity_id=other_entity.id,
                usn="USN999",
                full_name="Other Student",
            )
        )
        db.session.commit()

    res = client.get(f"/api/v1/entities/{entity_id}/leaderboard", headers=student_headers)
    assert res.status_code == 403
