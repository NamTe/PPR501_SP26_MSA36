from datetime import date
from typing import Union, Literal

from pydantic import BaseModel, EmailStr, Field


class StudentRequest(BaseModel):
    first_name: str | None = Field(default=None, title="Student's first name", description="Student's first name", max_length=500)
    last_name: str | None = Field(default=None, title="Student's last name", description="Student's last name", max_length=500)
    email: Union[EmailStr, Literal[""]] | None = Field(default=None, title="Email", description="Email", max_length=500)
    date_of_birth: Union[date, Literal[""]] | None = Field(default=None, title="DOB", description="Date of birth")
    home_town: str | None = Field(default=None, title="Hometown", description="Hometown", max_length=500)
    math_score: float | None = Field(default=None, title="Math Score", description="Math Score")
    literature_score: float | None = Field(default=None, title="Literature Score", description="Literature Score")
    english_score: float | None = Field(default=None, title="English Score", description="English Score")
