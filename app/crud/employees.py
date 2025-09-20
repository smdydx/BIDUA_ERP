from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.models import Employee, Attendance
from app.schemas.schemas import EmployeeRead

class CRUDEmployee(CRUDBase[Employee, Any, Any]):
    def get_by_emp_code(self, db: Session, *, emp_code: str) -> Optional[Employee]:
        return db.query(Employee).filter(Employee.emp_code == emp_code).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[Employee]:
        return db.query(Employee).filter(Employee.email == email).first()

employee = CRUDEmployee(Employee)

class CRUDAttendance(CRUDBase[Attendance, Any, Any]):
    def get_by_employee_date(self, db: Session, *, employee_id: int, date: str) -> Optional[Attendance]:
        return db.query(Attendance).filter(
            Attendance.employee_id == employee_id,
            Attendance.date == date
        ).first()

attendance = CRUDAttendance(Attendance)