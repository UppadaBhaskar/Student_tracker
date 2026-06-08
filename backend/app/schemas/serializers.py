from datetime import timezone

from marshmallow import Schema, fields


class UTCDateTime(fields.Field):
    """Serialize datetimes as ISO-8601 UTC with Z suffix for JavaScript."""

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        else:
            value = value.astimezone(timezone.utc)
        return value.isoformat().replace("+00:00", "Z")


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Str()
    role = fields.Str()


class SubjectSchema(Schema):
    id = fields.Int(dump_only=True)
    entity_id = fields.Int()
    name = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class EntitySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    entity_type = fields.Str()
    total_days = fields.Int()
    start_date = fields.Date()
    end_date = fields.Date()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class StudentSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int()
    entity_id = fields.Int()
    usn = fields.Str()
    full_name = fields.Str()
    college = fields.Str(allow_none=True)
    branch = fields.Str(allow_none=True)
    email = fields.Method("get_email")
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

    def get_email(self, obj):
        return obj.user.email if obj.user else None


class RemarkSchema(Schema):
    id = fields.Int()
    student_id = fields.Int()
    remark = fields.Str()
    created_at = fields.DateTime()


class DailyNoteResponseSchema(Schema):
    id = fields.Int()
    entity_id = fields.Int()
    day = fields.Int()
    notes = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class QuestionSchema(Schema):
    id = fields.Int()
    entity_id = fields.Int()
    question_number = fields.Int()
    subject_id = fields.Int()
    subject_name = fields.Method("get_subject_name")
    title = fields.Str()
    description = fields.Str(allow_none=True)
    day = fields.Int()
    timer_minutes = fields.Int()
    difficulty = fields.Method("get_difficulty")
    max_points = fields.Int()
    status = fields.Method("get_status")
    revealed_at = UTCDateTime(allow_none=True)
    created_at = UTCDateTime()
    updated_at = UTCDateTime()
    timer_remaining_seconds = fields.Method("get_timer_remaining")
    timer_expired = fields.Method("get_timer_expired")

    def get_subject_name(self, obj):
        return obj.subject.name if obj.subject else None

    def get_difficulty(self, obj):
        if obj.difficulty is None:
            return None
        return obj.difficulty.value if hasattr(obj.difficulty, "value") else str(obj.difficulty)

    def get_status(self, obj):
        if obj.status is None:
            return None
        return obj.status.value if hasattr(obj.status, "value") else str(obj.status)

    def get_timer_remaining(self, obj):
        from app.utils.datetime_utils import utc_now
        from app.utils.points import _ensure_utc

        if not obj.revealed_at:
            return None
        elapsed = (utc_now() - _ensure_utc(obj.revealed_at)).total_seconds()
        total = obj.timer_minutes * 60
        return max(0, int(total - elapsed))

    def get_timer_expired(self, obj):
        remaining = self.get_timer_remaining(obj)
        return remaining == 0 if remaining is not None else False


class AttemptSchema(Schema):
    id = fields.Int()
    question_id = fields.Int()
    student_id = fields.Int()
    student_name = fields.Method("get_student_name")
    clicked_at = UTCDateTime()
    approved_at = UTCDateTime(allow_none=True)
    status = fields.Method("get_status")
    click_rank = fields.Int()
    approved_rank = fields.Int(allow_none=True)
    points = fields.Int()
    trainer_notes = fields.Str(allow_none=True)
    created_at = UTCDateTime()

    def get_status(self, obj):
        if isinstance(obj, dict):
            return obj.get("status")
        if obj.status is None:
            return None
        return obj.status.value if hasattr(obj.status, "value") else str(obj.status)

    def get_student_name(self, obj):
        if isinstance(obj, dict):
            return obj.get("student_name")
        return obj.student.full_name if obj.student else None
