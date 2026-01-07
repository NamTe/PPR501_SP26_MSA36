from datetime import date

from pydantic import BaseModel, EmailStr, Field


class StudentRequest(BaseModel):
    first_name: str = Field(title="Student's first name", description="Student's first name", max_length=500)
    last_name: str = Field(title="Student's last name", description="Student's last name", max_length=500)
    email: EmailStr = Field(title="Email", description="Email", max_length=500)
    date_of_birth: date = Field(title="DOB", description="Date of birth")
    home_town: str = Field(title="Hometown", description="Hometown", max_length=500)
    math_score: float | None = Field(default=None, title="Math Score", description="Math Score")
    literature_score: float | None = Field(default=None, title="Literature Score", description="Literature Score")
    english_score: float | None = Field(default=None, title="English Score", description="English Score")
