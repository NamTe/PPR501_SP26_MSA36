from pydantic import BaseModel, EmailStr, Field
from typing import Annotated
from datetime import date


class StudentRequest(BaseModel):
    first_name: Annotated[str, Field(title="Student's first name", description="Student's first name", max_length=500)]
    last_name: Annotated[str, Field(title="Student's last name", description="Student's last name", max_length=500)]
    email: Annotated[EmailStr, Field(title="Email", description="Email", max_length=500)]
    date_of_birth: Annotated[date, Field(title="DOB", description="Date of birth")]
    home_town: Annotated[str, Field(title="Hometown", description="Hometown", max_length=500)]
    math_score: Annotated[float | None, Field(title="Math Score", description="Math Score")]
    literature_score: Annotated[float | None, Field(title="Literature Score", description="Literature Score")]
    english_score: Annotated[float | None, Field(title="English Score", description="English Score")]
