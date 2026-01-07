from pydantic import BaseModel, EmailStr, Field
from datetime import date


class StudentResponse(BaseModel):
    student_id: str = Field(title="Student's ID", description="Student's ID")
    first_name: str = Field(title="Student's first name", description="Student's first name")
    last_name: str = Field(title="Student's last name", description="Student's last name")
    email: EmailStr = Field(title="Email", description="Email")
    date_of_birth: date = Field(title="DOB", description="Date of birth")
    home_town: str = Field(title="Hometown", description="Hometown")
    math_score: float | None = Field(default=None, title="Math Score", description="Math Score")
    literature_score: float | None = Field(default=None, title="Literature Score", description="Literature Score")
    english_score: float | None = Field(default=None, title="English Score", description="English Score")

    model_config = {
        "from_attributes": True
    }
