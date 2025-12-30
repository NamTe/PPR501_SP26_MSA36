from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class StudentResponse(BaseModel):
    student_id: str
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    date_of_birth: Optional[date] = None
    home_town: Optional[str] = None
    math_score: Optional[float] = None
    literature_score: Optional[float] = None
    english_score: Optional[float] = None