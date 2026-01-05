from sqlmodel import Field, SQLModel


class Student(SQLModel, table=True):
    student_id: str | None = Field(default=None, primary_key=True)
    first_name: str = Field(index=False)
    last_name: str = Field(index=False)
    email: str = Field(index=False)
    date_of_birth: str = Field(index=False)
    home_town: str = Field(index=False)
    math_score: float | None = Field(index=False)
    literature_score: float | None = Field(index=False)
    english_score: float | None = Field(index=False)