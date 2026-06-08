from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import get_jwt, jwt_required
import io

from app.exceptions import AppException
from app.schemas.serializers import (
    DailyNoteResponseSchema,
    EntitySchema,
    QuestionSchema,
    RemarkSchema,
    StudentSchema,
    SubjectSchema,
)
from app.schemas.validation import validate_payload
from app.schemas.validation import (
    AssignmentBulkSchema,
    AttemptActionSchema,
    AttendanceBulkSchema,
    DailyNoteSchema,
    EntityCreateSchema,
    EntityUpdateSchema,
    LoginSchema,
    PresentationBulkSchema,
    QuestionCreateSchema,
    QuestionUpdateSchema,
    RemarkCreateSchema,
    StudentCreateSchema,
    StudentUpdateSchema,
    SubjectCreateSchema,
    SubjectUpdateSchema,
    TestScoreBulkSchema,
)
from app.services.analytics_service import AnalyticsService
from app.services.attempt_service import AttemptService
from app.services.auth_service import AuthService
from app.services.daily_notes_service import DailyNotesService
from app.services.dashboard_service import DashboardService
from app.services.entity_service import EntityService
from app.services.excel_service import ExcelService
from app.services.leaderboard_service import LeaderboardService
from app.services.question_service import QuestionService
from app.services.question_stats_service import QuestionStatsService
from app.services.remarks_service import RemarksService
from app.services.risk_service import RiskService
from app.services.student_service import StudentService
from app.services.student_trend_service import StudentTrendService
from app.services.test_score_service import TestScoreService
from app.services.tracking_service import TrackingService
from app.utils.decorators import role_required

auth_bp = Blueprint("auth", __name__)
entities_bp = Blueprint("entities", __name__)
students_bp = Blueprint("students", __name__)
tracking_bp = Blueprint("tracking", __name__)
questions_bp = Blueprint("questions", __name__)
attempts_bp = Blueprint("attempts", __name__)
analytics_bp = Blueprint("analytics", __name__)


def _success(data=None, status=200):
    return jsonify({"success": True, "data": data}), status


def _error_handler(e: AppException):
    return jsonify({"success": False, "error": e.message}), e.status_code


@auth_bp.app_errorhandler(AppException)
def handle_app_exception(e):
    return _error_handler(e)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = validate_payload(LoginSchema, request.get_json())
    result = AuthService().login(data["email"], data["password"])
    return _success(result)


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    claims = get_jwt()
    result = AuthService().get_me(claims["user_id"])
    return _success(result)


@entities_bp.route("", methods=["GET"])
@jwt_required()
@role_required("trainer")
def list_entities():
    entities = EntityService().list_entities()
    return _success(EntitySchema(many=True).dump(entities))


@entities_bp.route("", methods=["POST"])
@jwt_required()
@role_required("trainer")
def create_entity():
    data = validate_payload(EntityCreateSchema, request.get_json())
    entity = EntityService().create_entity(data)
    return _success(EntitySchema().dump(entity), 201)


@entities_bp.route("/<int:entity_id>", methods=["GET"])
@jwt_required()
@role_required("trainer")
def get_entity(entity_id):
    entity = EntityService().get_entity(entity_id)
    return _success(EntitySchema().dump(entity))


@entities_bp.route("/<int:entity_id>", methods=["PUT"])
@jwt_required()
@role_required("trainer")
def update_entity(entity_id):
    data = validate_payload(EntityUpdateSchema, request.get_json())
    entity = EntityService().update_entity(entity_id, data)
    return _success(EntitySchema().dump(entity))


@entities_bp.route("/<int:entity_id>", methods=["DELETE"])
@jwt_required()
@role_required("trainer")
def delete_entity(entity_id):
    EntityService().delete_entity(entity_id)
    return _success({"deleted": True})


@entities_bp.route("/<int:entity_id>/subjects", methods=["GET"])
@jwt_required()
@role_required("trainer")
def list_subjects(entity_id):
    subjects = EntityService().list_subjects(entity_id)
    return _success(SubjectSchema(many=True).dump(subjects))


@entities_bp.route("/<int:entity_id>/subjects", methods=["POST"])
@jwt_required()
@role_required("trainer")
def create_subject(entity_id):
    data = validate_payload(SubjectCreateSchema, request.get_json())
    subject = EntityService().create_subject(entity_id, data["name"])
    return _success(SubjectSchema().dump(subject), 201)


@entities_bp.route("/<int:entity_id>/students", methods=["GET"])
@jwt_required()
@role_required("trainer")
def list_students(entity_id):
    students = StudentService().list_students(entity_id)
    return _success(StudentSchema(many=True).dump(students))


@entities_bp.route("/<int:entity_id>/students", methods=["POST"])
@jwt_required()
@role_required("trainer")
def create_student(entity_id):
    data = validate_payload(StudentCreateSchema, request.get_json())
    student = StudentService().create_student(entity_id, data)
    return _success(StudentSchema().dump(student), 201)


@entities_bp.route("/<int:entity_id>/students/import", methods=["POST"])
@jwt_required()
@role_required("trainer")
def import_students(entity_id):
    if "file" not in request.files:
        from app.exceptions import ValidationException
        raise ValidationException("No file uploaded")
    result = ExcelService().import_students(entity_id, request.files["file"].read())
    return _success(result)


@entities_bp.route("/<int:entity_id>/students/export", methods=["GET"])
@jwt_required()
@role_required("trainer")
def export_students(entity_id):
    content, filename = ExcelService().export(entity_id, "students")
    return send_file(io.BytesIO(content), download_name=filename, as_attachment=True)


@entities_bp.route("/<int:entity_id>/daily-notes", methods=["GET"])
@jwt_required()
@role_required("trainer")
def get_daily_notes(entity_id):
    day = request.args.get("day", type=int)
    notes = DailyNotesService().get_notes(entity_id, day)
    return _success(DailyNoteResponseSchema(many=True).dump(notes))


@entities_bp.route("/<int:entity_id>/daily-notes/<int:day>", methods=["PUT"])
@jwt_required()
@role_required("trainer")
def upsert_daily_note(entity_id, day):
    data = validate_payload(DailyNoteSchema, request.get_json())
    note = DailyNotesService().upsert_note(entity_id, day, data["notes"])
    return _success(DailyNoteResponseSchema().dump(note))


@entities_bp.route("/<int:entity_id>/attendance", methods=["GET"])
@jwt_required()
@role_required("trainer")
def get_attendance(entity_id):
    day = request.args.get("day", type=int)
    from app.exceptions import ValidationException
    if not day:
        raise ValidationException("day query parameter is required")
    records = TrackingService().get_attendance(entity_id, day)
    return _success([{"student_id": r.student_id, "status": r.status.value} for r in records])


@entities_bp.route("/<int:entity_id>/attendance", methods=["PUT"])
@jwt_required()
@role_required("trainer")
def upsert_attendance(entity_id):
    day = request.args.get("day", type=int)
    from app.exceptions import ValidationException
    if not day:
        raise ValidationException("day query parameter is required")
    data = validate_payload(AttendanceBulkSchema, request.get_json())
    records = TrackingService().upsert_attendance(entity_id, day, data["records"])
    return _success([{"student_id": r.student_id, "status": r.status.value} for r in records])


@entities_bp.route("/<int:entity_id>/assignments", methods=["GET"])
@jwt_required()
@role_required("trainer")
def get_assignments(entity_id):
    day = request.args.get("day", type=int)
    from app.exceptions import ValidationException
    if not day:
        raise ValidationException("day query parameter is required")
    records = TrackingService().get_assignments(entity_id, day)
    return _success([{"student_id": r.student_id, "status": r.status.value} for r in records])


@entities_bp.route("/<int:entity_id>/assignments", methods=["PUT"])
@jwt_required()
@role_required("trainer")
def upsert_assignments(entity_id):
    day = request.args.get("day", type=int)
    from app.exceptions import ValidationException
    if not day:
        raise ValidationException("day query parameter is required")
    data = validate_payload(AssignmentBulkSchema, request.get_json())
    records = TrackingService().upsert_assignments(entity_id, day, data["records"])
    return _success([{"student_id": r.student_id, "status": r.status.value} for r in records])


@entities_bp.route("/<int:entity_id>/presentations", methods=["GET"])
@jwt_required()
@role_required("trainer")
def get_presentations(entity_id):
    day = request.args.get("day", type=int)
    records = TrackingService().get_presentations(entity_id, day)
    return _success(
        [
            {
                "student_id": r.student_id,
                "subject_id": r.subject_id,
                "day": r.day,
                "score": r.score,
            }
            for r in records
        ]
    )


@entities_bp.route("/<int:entity_id>/presentations", methods=["PUT"])
@jwt_required()
@role_required("trainer")
def upsert_presentations(entity_id):
    data = validate_payload(PresentationBulkSchema, request.get_json())
    records = TrackingService().upsert_presentations(entity_id, data["records"])
    return _success({"updated": len(records)})


@entities_bp.route("/<int:entity_id>/test-scores", methods=["GET"])
@jwt_required()
@role_required("trainer")
def get_test_scores(entity_id):
    records = TestScoreService().list_scores(entity_id)
    return _success(
        [
            {
                "student_id": r.student_id,
                "subject_id": r.subject_id,
                "day": r.day,
                "score": r.score,
            }
            for r in records
        ]
    )


@entities_bp.route("/<int:entity_id>/test-scores", methods=["PUT"])
@jwt_required()
@role_required("trainer")
def upsert_test_scores(entity_id):
    data = validate_payload(TestScoreBulkSchema, request.get_json())
    records = TestScoreService().upsert_scores(entity_id, data["records"])
    return _success({"updated": len(records)})


@entities_bp.route("/<int:entity_id>/test-scores/import", methods=["POST"])
@jwt_required()
@role_required("trainer")
def import_test_scores(entity_id):
    if "file" not in request.files:
        from app.exceptions import ValidationException
        raise ValidationException("No file uploaded")
    result = ExcelService().import_test_scores(entity_id, request.files["file"].read())
    return _success(result)


@entities_bp.route("/<int:entity_id>/questions", methods=["GET"])
@jwt_required()
@role_required("trainer")
def list_questions(entity_id):
    questions = QuestionService().list_questions(entity_id)
    return _success(QuestionSchema(many=True).dump(questions))


@entities_bp.route("/<int:entity_id>/questions", methods=["POST"])
@jwt_required()
@role_required("trainer")
def create_question(entity_id):
    data = validate_payload(QuestionCreateSchema, request.get_json())
    question = QuestionService().create_question(entity_id, data)
    return _success(QuestionSchema().dump(question), 201)


@entities_bp.route("/<int:entity_id>/question-statistics", methods=["GET"])
@jwt_required()
@role_required("trainer")
def question_statistics(entity_id):
    stats = QuestionStatsService().stats_for_entity(entity_id)
    return _success(stats)


@entities_bp.route("/<int:entity_id>/leaderboard", methods=["GET"])
@jwt_required()
def entity_leaderboard(entity_id):
    claims = get_jwt()
    if claims.get("role") == "student":
        student = StudentService().get_by_user_id(claims["user_id"])
        if student.entity_id != entity_id:
            from app.exceptions import ForbiddenException
            raise ForbiddenException("Access denied to this entity")
    subject_id = request.args.get("subject_id")
    sid = None if not subject_id or subject_id == "all" else int(subject_id)
    board = LeaderboardService().get_leaderboard(entity_id, sid)
    return _success(board)


@entities_bp.route("/<int:entity_id>/at-risk-students", methods=["GET"])
@jwt_required()
@role_required("trainer")
def at_risk_students(entity_id):
    level = request.args.get("level", "all")
    levels = ("yellow", "red") if level == "all" else (level,)
    students = RiskService().list_at_risk_students(entity_id, levels=levels)
    return _success(students)


@entities_bp.route("/<int:entity_id>/trainer-dashboard", methods=["GET"])
@jwt_required()
@role_required("trainer")
def trainer_dashboard(entity_id):
    data = DashboardService().trainer_dashboard(entity_id)
    return _success(data)


@entities_bp.route("/<int:entity_id>/analytics", methods=["GET"])
@jwt_required()
@role_required("trainer")
def analytics(entity_id):
    day = request.args.get("day", "all")
    day_filter = int(day) if day != "all" else "all"
    data = AnalyticsService().get_analytics(entity_id, day_filter)
    return _success(data)


@entities_bp.route("/<int:entity_id>/daily-summary", methods=["GET"])
@jwt_required()
@role_required("trainer")
def daily_summary(entity_id):
    day = request.args.get("day", "all")
    day_filter = int(day) if day != "all" else "all"
    data = AnalyticsService().get_daily_summary(entity_id, day_filter)
    return _success(data)


@entities_bp.route("/import-templates/<template_type>", methods=["GET"])
@jwt_required()
@role_required("trainer")
def import_template(template_type):
    content, filename = ExcelService().export_template(template_type)
    return send_file(
        io.BytesIO(content),
        download_name=filename,
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@entities_bp.route("/<int:entity_id>/export/<export_type>", methods=["GET"])
@jwt_required()
@role_required("trainer")
def export_data(entity_id, export_type):
    content, filename = ExcelService().export(entity_id, export_type)
    return send_file(
        io.BytesIO(content),
        download_name=filename,
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@students_bp.route("/<int:student_id>", methods=["GET"])
@jwt_required()
@role_required("trainer")
def get_student(student_id):
    from app.services.risk_service import RiskService

    profile = StudentService().get_student_profile(student_id)
    risk = RiskService().assess_student(student_id)
    return _success(
        {
            "student": StudentSchema().dump(profile["student"]),
            "remarks": RemarkSchema(many=True).dump(profile["remarks"]),
            "risk": risk,
        }
    )


@students_bp.route("/<int:student_id>", methods=["PUT"])
@jwt_required()
@role_required("trainer")
def update_student(student_id):
    data = validate_payload(StudentUpdateSchema, request.get_json())
    student = StudentService().update_student(student_id, data)
    return _success(StudentSchema().dump(student))


@students_bp.route("/<int:student_id>", methods=["DELETE"])
@jwt_required()
@role_required("trainer")
def delete_student(student_id):
    StudentService().delete_student(student_id)
    return _success({"deleted": True})


@students_bp.route("/<int:student_id>/remarks", methods=["GET"])
@jwt_required()
@role_required("trainer")
def list_remarks(student_id):
    remarks = RemarksService().list_remarks(student_id)
    return _success(RemarkSchema(many=True).dump(remarks))


@students_bp.route("/<int:student_id>/remarks", methods=["POST"])
@jwt_required()
@role_required("trainer")
def add_remark(student_id):
    data = validate_payload(RemarkCreateSchema, request.get_json())
    remark = RemarksService().add_remark(student_id, data["remark"])
    return _success(RemarkSchema().dump(remark), 201)


@students_bp.route("/<int:student_id>/performance-trends", methods=["GET"])
@jwt_required()
@role_required("trainer")
def student_performance_trends(student_id):
    trends = StudentTrendService().get_trends(student_id)
    return _success(trends)


@students_bp.route("/me/dashboard", methods=["GET"])
@jwt_required()
@role_required("student")
def student_dashboard():
    claims = get_jwt()
    student = StudentService().get_by_user_id(claims["user_id"])
    data = DashboardService().student_dashboard(student.id)
    return _success(data)


@students_bp.route("/me/performance-trends", methods=["GET"])
@jwt_required()
@role_required("student")
def my_performance_trends():
    claims = get_jwt()
    student = StudentService().get_by_user_id(claims["user_id"])
    trends = StudentTrendService().get_trends(student.id)
    return _success(trends)


@students_bp.route("/me/question-history", methods=["GET"])
@jwt_required()
@role_required("student")
def my_question_history():
    claims = get_jwt()
    student = StudentService().get_by_user_id(claims["user_id"])
    history = AttemptService().get_question_history(student.id)
    return _success(history)


@students_bp.route("/me/question-history/<int:question_id>/attempts", methods=["GET"])
@jwt_required()
@role_required("student")
def my_question_attempts(question_id):
    claims = get_jwt()
    student = StudentService().get_by_user_id(claims["user_id"])
    attempts = AttemptService().get_question_attempts_detail(student.id, question_id)
    return _success(attempts)


@questions_bp.route("/<int:question_id>", methods=["PUT"])
@jwt_required()
@role_required("trainer")
def update_question(question_id):
    data = validate_payload(QuestionUpdateSchema, request.get_json())
    question = QuestionService().update_question(question_id, data)
    return _success(QuestionSchema().dump(question))


@questions_bp.route("/<int:question_id>", methods=["DELETE"])
@jwt_required()
@role_required("trainer")
def delete_question(question_id):
    QuestionService().delete_question(question_id)
    return _success({"deleted": True})


@questions_bp.route("/<int:question_id>/reveal", methods=["POST"])
@jwt_required()
@role_required("trainer")
def reveal_question(question_id):
    question = QuestionService().reveal_question(question_id)
    return _success(QuestionSchema().dump(question))


@questions_bp.route("/<int:question_id>/archive", methods=["POST"])
@jwt_required()
@role_required("trainer")
def archive_question(question_id):
    question = QuestionService().archive_question(question_id)
    return _success(QuestionSchema().dump(question))


@questions_bp.route("/active", methods=["GET"])
@jwt_required()
def get_active_question():
    question = QuestionService().get_active_question()
    payload = QuestionSchema().dump(question) if question else None
    claims = get_jwt()
    latest_attempt = None
    if question and claims.get("role") == "student":
        student = StudentService().get_by_user_id(claims["user_id"])
        attempts = AttemptService().get_question_attempts_detail(student.id, question.id)
        latest_attempt = attempts[-1] if attempts else None
    return _success({"question": payload, "latest_attempt": latest_attempt})


@questions_bp.route("/active/complete", methods=["POST"])
@jwt_required()
@role_required("student")
def complete_active_question():
    claims = get_jwt()
    attempt = AttemptService().complete_active_question(claims["user_id"])
    return _success(attempt, 201)


@questions_bp.route("/import", methods=["POST"])
@jwt_required()
@role_required("trainer")
def import_questions():
    entity_id = request.args.get("entity_id", type=int)
    from app.exceptions import ValidationException
    if not entity_id:
        raise ValidationException("entity_id query parameter is required")
    if "file" not in request.files:
        raise ValidationException("No file uploaded")
    result = ExcelService().import_questions(entity_id, request.files["file"].read())
    return _success(result)


@questions_bp.route("/<int:question_id>/attempts", methods=["GET"])
@jwt_required()
@role_required("trainer")
def list_question_attempts(question_id):
    status = request.args.get("status")
    attempts = AttemptService().list_attempts(question_id, status)
    return _success(attempts)


@questions_bp.route("/<int:question_id>/statistics", methods=["GET"])
@jwt_required()
@role_required("trainer")
def single_question_stats(question_id):
    stats = QuestionStatsService().stats_for_question(question_id)
    return _success(stats)


@attempts_bp.route("/<int:attempt_id>/approve", methods=["POST"])
@jwt_required()
@role_required("trainer")
def approve_attempt(attempt_id):
    data = validate_payload(AttemptActionSchema, request.get_json(silent=True) or {})
    result = AttemptService().approve_attempt(attempt_id, data.get("trainer_notes"))
    return _success(result)


@attempts_bp.route("/<int:attempt_id>/reject", methods=["POST"])
@jwt_required()
@role_required("trainer")
def reject_attempt(attempt_id):
    data = validate_payload(AttemptActionSchema, request.get_json(silent=True) or {})
    result = AttemptService().reject_attempt(attempt_id, data.get("trainer_notes"))
    return _success(result)


@entities_bp.route("/subjects/<int:subject_id>", methods=["PUT"])
@jwt_required()
@role_required("trainer")
def update_subject(subject_id):
    data = validate_payload(SubjectUpdateSchema, request.get_json())
    subject = EntityService().update_subject(subject_id, data["name"])
    return _success(SubjectSchema().dump(subject))


@entities_bp.route("/subjects/<int:subject_id>", methods=["DELETE"])
@jwt_required()
@role_required("trainer")
def delete_subject(subject_id):
    EntityService().delete_subject(subject_id)
    return _success({"deleted": True})


@analytics_bp.route("/health", methods=["GET"])
def health():
    return _success({"status": "ok"})
