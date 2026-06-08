from marshmallow import Schema, fields, validate


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))


class EntityCreateSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    entity_type = fields.String(
        required=True, validate=validate.OneOf(["workshop", "bootcamp", "training_program"])
    )
    total_days = fields.Integer(required=True, validate=validate.Range(min=1))
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)


class EntityUpdateSchema(Schema):
    name = fields.String(validate=validate.Length(min=1, max=255))
    entity_type = fields.String(
        validate=validate.OneOf(["workshop", "bootcamp", "training_program"])
    )
    total_days = fields.Integer(validate=validate.Range(min=1))
    start_date = fields.Date()
    end_date = fields.Date()


class SubjectCreateSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=255))


class SubjectUpdateSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=255))


class StudentCreateSchema(Schema):
    usn = fields.String(required=True, validate=validate.Length(min=1, max=50))
    full_name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    college = fields.String(allow_none=True)
    branch = fields.String(allow_none=True)
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))


class StudentUpdateSchema(Schema):
    usn = fields.String(validate=validate.Length(min=1, max=50))
    full_name = fields.String(validate=validate.Length(min=1, max=255))
    college = fields.String(allow_none=True)
    branch = fields.String(allow_none=True)
    email = fields.Email()
    password = fields.String(validate=validate.Length(min=6))


class RemarkCreateSchema(Schema):
    remark = fields.String(required=True, validate=validate.Length(min=1))


class DailyNoteSchema(Schema):
    notes = fields.String(required=True, validate=validate.Length(min=1))


class AttendanceItemSchema(Schema):
    student_id = fields.Integer(required=True)
    status = fields.String(required=True, validate=validate.OneOf(["present", "absent"]))


class AttendanceBulkSchema(Schema):
    records = fields.List(fields.Nested(AttendanceItemSchema), required=True)


class AssignmentItemSchema(Schema):
    student_id = fields.Integer(required=True)
    status = fields.String(required=True, validate=validate.OneOf(["completed", "not_completed"]))


class AssignmentBulkSchema(Schema):
    records = fields.List(fields.Nested(AssignmentItemSchema), required=True)


class PresentationScoreItemSchema(Schema):
    student_id = fields.Integer(required=True)
    subject_id = fields.Integer(required=True)
    day = fields.Integer(required=True, validate=validate.Range(min=1))
    score = fields.Float(required=True)


class PresentationBulkSchema(Schema):
    records = fields.List(fields.Nested(PresentationScoreItemSchema), required=True)


class TestScoreItemSchema(Schema):
    student_id = fields.Integer(required=True)
    subject_id = fields.Integer(required=True)
    day = fields.Integer(required=True, validate=validate.Range(min=1))
    score = fields.Float(required=True)


class TestScoreBulkSchema(Schema):
    records = fields.List(fields.Nested(TestScoreItemSchema), required=True)


class QuestionCreateSchema(Schema):
    question_number = fields.Integer(required=True, validate=validate.Range(min=1))
    subject_id = fields.Integer(required=True)
    title = fields.String(required=True, validate=validate.Length(min=1, max=255))
    description = fields.String(allow_none=True)
    day = fields.Integer(required=True, validate=validate.Range(min=1))
    timer_minutes = fields.Integer(required=True, validate=validate.Range(min=1))
    difficulty = fields.String(
        load_default="medium", validate=validate.OneOf(["easy", "medium", "hard"])
    )
    max_points = fields.Integer(validate=validate.Range(min=1))


class QuestionUpdateSchema(Schema):
    question_number = fields.Integer(validate=validate.Range(min=1))
    subject_id = fields.Integer()
    title = fields.String(validate=validate.Length(min=1, max=255))
    description = fields.String(allow_none=True)
    day = fields.Integer(validate=validate.Range(min=1))
    timer_minutes = fields.Integer(validate=validate.Range(min=1))
    difficulty = fields.String(validate=validate.OneOf(["easy", "medium", "hard"]))
    max_points = fields.Integer(validate=validate.Range(min=1))


class AttemptActionSchema(Schema):
    trainer_notes = fields.String(allow_none=True)


def validate_payload(schema_class, data: dict) -> dict:
    from app.exceptions import ValidationException

    schema = schema_class()
    errors = schema.validate(data or {})
    if errors:
        raise ValidationException(str(errors))
    return schema.load(data or {})
