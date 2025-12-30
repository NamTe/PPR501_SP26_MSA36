from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Annotated
from datetime import date

class StudentRequest(BaseModel):
    first_name: Annotated[str , Field(title="Student first name", max_length=10)]
    last_name: str
    email: Optional[EmailStr] = None
    date_of_birth: Optional[date] = None
    home_town: Optional[str] = None
    math_score: Optional[float] = None
    literature_score: Optional[float] = None
    english_score: Optional[float] = None