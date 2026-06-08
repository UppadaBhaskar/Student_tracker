import io
from typing import Any

import pandas as pd

from app.exceptions import ValidationException
from app.models.enums import UserRole
from app.repositories.entity_repository import SubjectRepository
from app.services.analytics_service import AnalyticsService
from app.services.attempt_service import AttemptService
from app.services.auth_service import AuthService
from app.services.entity_service import EntityService
from app.services.leaderboard_service import LeaderboardService
from app.services.question_service import QuestionService
from app.services.rank_service import RankService
from app.services.student_service import StudentService
from app.services.tracking_service import TrackingService


class ExcelService:
    EXPORT_TYPES = {
        "students",
        "attendance",
        "assignments",
        "presentations",
        "test-scores",
        "question-results",
        "question-attempts",
        "leaderboard",
        "analytics-summary",
    }

    IMPORT_TEMPLATE_TYPES = {
        "students",
        "questions",
        "test-scores",
    }

    TEMPLATE_COLUMNS = {
        "students": ["USN", "Name", "College", "Branch", "Email", "Password"],
        "questions": ["Question Number", "Subject", "Question", "Day", "Timer", "Difficulty"],
        "test-scores": ["Student", "Subject", "Day", "Score"],
    }

    def __init__(self):
        self.student_service = StudentService()
        self.tracking_service = TrackingService()
        self.entity_service = EntityService()
        self.question_service = QuestionService()
        self.attempt_service = AttemptService()
        self.leaderboard_service = LeaderboardService()
        self.analytics_service = AnalyticsService()
        self.rank_service = RankService()
        self.auth_service = AuthService()
        self.subject_repo = SubjectRepository()

    def import_students(self, entity_id: int, file_bytes: bytes) -> dict:
        df = pd.read_excel(io.BytesIO(file_bytes))
        required = {"USN", "Name", "Email", "Password"}
        columns = set(df.columns)
        if not required.issubset(columns):
            raise ValidationException(f"Missing columns. Required: {required}")

        created = []
        errors = []
        for idx, row in df.iterrows():
            try:
                data = {
                    "usn": str(row["USN"]).strip(),
                    "full_name": str(row["Name"]).strip(),
                    "college": str(row["College"]).strip() if "College" in df.columns and pd.notna(row.get("College")) else None,
                    "branch": str(row["Branch"]).strip() if "Branch" in df.columns and pd.notna(row.get("Branch")) else None,
                    "email": str(row["Email"]).strip(),
                    "password": str(row["Password"]).strip(),
                }
                if len(data["password"]) < 6:
                    raise ValidationException("Password must be at least 6 characters")
                student = self.student_service.create_student(entity_id, data)
                created.append(student.id)
            except Exception as exc:
                errors.append({"row": idx + 2, "error": str(getattr(exc, "message", exc))})
        return {"created": len(created), "errors": errors}

    def import_questions(self, entity_id: int, file_bytes: bytes) -> dict:
        df = pd.read_excel(io.BytesIO(file_bytes))
        required = {"Question Number", "Subject", "Question", "Day", "Timer"}
        if not required.issubset(set(df.columns)):
            raise ValidationException(f"Missing columns. Required: {required}")

        created = []
        errors = []
        for idx, row in df.iterrows():
            try:
                subject_name = str(row["Subject"]).strip()
                subject = self.subject_repo.get_by_entity_and_name(entity_id, subject_name)
                if not subject:
                    raise ValidationException(f"Subject '{subject_name}' not found")

                data = {
                    "question_number": int(row["Question Number"]),
                    "subject_id": subject.id,
                    "title": str(row["Question"]).strip(),
                    "day": int(row["Day"]),
                    "timer_minutes": int(row["Timer"]),
                }
                if "Difficulty" in df.columns and pd.notna(row.get("Difficulty")):
                    data["difficulty"] = str(row["Difficulty"]).strip().lower()

                q = self.question_service.create_question(entity_id, data)
                created.append(q.id)
            except Exception as exc:
                errors.append({"row": idx + 2, "error": str(getattr(exc, "message", exc))})
        return {"created": len(created), "errors": errors}

    def import_test_scores(self, entity_id: int, file_bytes: bytes) -> dict:
        from app.services.test_score_service import TestScoreService

        df = pd.read_excel(io.BytesIO(file_bytes))
        required = {"Student", "Subject", "Day", "Score"}
        if not required.issubset(set(df.columns)):
            raise ValidationException(f"Missing columns. Required: {required}")

        test_service = TestScoreService()
        records = []
        errors = []
        students = {s.full_name: s for s in self.student_service.list_students(entity_id)}

        for idx, row in df.iterrows():
            try:
                student_name = str(row["Student"]).strip()
                subject_name = str(row["Subject"]).strip()
                student = students.get(student_name)
                if not student:
                    raise ValidationException(f"Student '{student_name}' not found")
                subject = self.subject_repo.get_by_entity_and_name(entity_id, subject_name)
                if not subject:
                    raise ValidationException(f"Subject '{subject_name}' not found")
                records.append(
                    {
                        "student_id": student.id,
                        "subject_id": subject.id,
                        "day": int(row["Day"]),
                        "score": float(row["Score"]),
                    }
                )
            except Exception as exc:
                errors.append({"row": idx + 2, "error": str(getattr(exc, "message", exc))})

        if records:
            test_service.upsert_scores(entity_id, records)
        return {"imported": len(records), "errors": errors}

    def export(self, entity_id: int, export_type: str) -> tuple[bytes, str]:
        if export_type not in self.EXPORT_TYPES:
            raise ValidationException(f"Invalid export type. Valid: {self.EXPORT_TYPES}")

        filename = f"{export_type}_{entity_id}.xlsx"
        if export_type == "students":
            df = self._export_students(entity_id)
        elif export_type == "attendance":
            df = self._export_attendance(entity_id)
        elif export_type == "assignments":
            df = self._export_assignments(entity_id)
        elif export_type == "presentations":
            df = self._export_presentations(entity_id)
        elif export_type == "test-scores":
            df = self._export_test_scores(entity_id)
        elif export_type == "question-results":
            df = self._export_question_results(entity_id)
        elif export_type == "question-attempts":
            df = self._export_question_attempts(entity_id)
        elif export_type == "leaderboard":
            df = self._export_leaderboard(entity_id)
        else:
            df = self._export_analytics_summary(entity_id)

        output = io.BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        return output.read(), filename

    def export_template(self, template_type: str) -> tuple[bytes, str]:
        if template_type not in self.IMPORT_TEMPLATE_TYPES:
            raise ValidationException(
                f"Invalid template type. Valid: {self.IMPORT_TEMPLATE_TYPES}"
            )
        df = pd.DataFrame(columns=self.TEMPLATE_COLUMNS[template_type])
        output = io.BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        filename = f"{template_type}_template.xlsx"
        return output.read(), filename

    def _export_students(self, entity_id: int) -> pd.DataFrame:
        students = self.student_service.list_students(entity_id)
        return pd.DataFrame(
            [
                {
                    "USN": s.usn,
                    "Name": s.full_name,
                    "College": s.college,
                    "Branch": s.branch,
                    "Email": s.user.email,
                }
                for s in students
            ]
        )

    def _export_attendance(self, entity_id: int) -> pd.DataFrame:
        records = self.tracking_service.attendance_repo.list_by_entity(entity_id)
        return pd.DataFrame(
            [{"Student ID": r.student_id, "Day": r.day, "Status": r.status.value} for r in records]
        )

    def _export_assignments(self, entity_id: int) -> pd.DataFrame:
        records = self.tracking_service.assignment_repo.list_by_entity(entity_id)
        return pd.DataFrame(
            [{"Student ID": r.student_id, "Day": r.day, "Status": r.status.value} for r in records]
        )

    def _export_presentations(self, entity_id: int) -> pd.DataFrame:
        records = self.tracking_service.presentation_repo.list_by_entity_day(entity_id)
        return pd.DataFrame(
            [
                {
                    "Student ID": r.student_id,
                    "Subject ID": r.subject_id,
                    "Day": r.day,
                    "Score": r.score,
                }
                for r in records
            ]
        )

    def _export_test_scores(self, entity_id: int) -> pd.DataFrame:
        from app.services.test_score_service import TestScoreService
        records = TestScoreService().list_scores(entity_id)
        return pd.DataFrame(
            [
                {
                    "Student ID": r.student_id,
                    "Subject ID": r.subject_id,
                    "Day": r.day,
                    "Score": r.score,
                }
                for r in records
            ]
        )

    def _export_question_results(self, entity_id: int) -> pd.DataFrame:
        history = []
        for s in self.student_service.list_students(entity_id):
            for item in self.attempt_service.get_question_history(s.id):
                history.append(
                    {
                        "Student ID": s.id,
                        "Question": item["title"],
                        "Approved Rank": item["approved_rank"],
                        "Points": item["points"],
                        "Status": item["final_status"],
                    }
                )
        return pd.DataFrame(history)

    def _export_question_attempts(self, entity_id: int) -> pd.DataFrame:
        rows = []
        for q in self.question_service.list_questions(entity_id):
            for a in self.attempt_service.list_attempts(q.id):
                rows.append(
                    {
                        "Question": q.title,
                        "Student": a["student_name"],
                        "Click Rank": a["click_rank"],
                        "Approved Rank": a["approved_rank"],
                        "Points": a["points"],
                        "Status": a["status"],
                        "Clicked At": a["clicked_at"],
                    }
                )
        return pd.DataFrame(rows)

    def _export_leaderboard(self, entity_id: int) -> pd.DataFrame:
        board = self.leaderboard_service.get_leaderboard(entity_id)
        return pd.DataFrame(board)

    def _export_analytics_summary(self, entity_id: int) -> pd.DataFrame:
        summary = self.analytics_service.get_daily_summary(entity_id)
        return pd.DataFrame(summary["days"])
