from app.models.student_remarks import StudentRemark
from app.repositories.student_repository import StudentRemarkRepository
from app.services.student_service import StudentService


class RemarksService:
    def __init__(self):
        self.remark_repo = StudentRemarkRepository()
        self.student_service = StudentService()

    def list_remarks(self, student_id: int) -> list[StudentRemark]:
        self.student_service.get_student(student_id)
        return self.remark_repo.list_by_student(student_id)

    def add_remark(self, student_id: int, remark: str) -> StudentRemark:
        self.student_service.get_student(student_id)
        record = StudentRemark(student_id=student_id, remark=remark.strip())
        self.remark_repo.add(record)
        self.remark_repo.commit()
        return record
