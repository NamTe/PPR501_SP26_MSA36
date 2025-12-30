import random
import uuid

from fastapi import APIRouter
from starlette import status
from pydantic import EmailStr
from schemas import StudentRequest, StudentResponse
from typing import cast
from datetime import date

router = APIRouter(
    prefix='/v1/api'
)


@router.post("/students", status_code=status.HTTP_201_CREATED, summary="Create a new student")
def create_student(
        payload: StudentRequest) -> StudentResponse:
    student_id = f"MSA36{str(uuid.uuid4())[:8]}"
    student = StudentResponse(student_id=student_id, **payload.model_dump())
    return student


@router.put("/students/{student_id}", summary="Update a student")
def update_student(student_id: str, payload: StudentRequest) -> StudentResponse:
    student = StudentResponse(student_id=student_id, **payload.model_dump())
    return student


@router.delete("/students/{student_id}", summary="Delete a student", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: str) -> None:
    print(student_id)
    return


@router.get("/students", summary="Get all students")
def get_students() -> list[StudentResponse]:
    lst = list()
    for i in range(1, 10):
        lst.append(StudentResponse(
            student_id=f"MSA36{str(uuid.uuid4())[:8]}",
            first_name=random.choice(["Nam", "An", "Hang", "Tuan", "Lam", "Ninh", "Lan"]),
            last_name=random.choice(["Nguyen", "Trinh", "Le", "Vu", "Ton"]),
            email=cast(EmailStr, "example@gmail.com"),
            date_of_birth=cast(date, "2025-12-31"),
            home_town=random.choice(["Bac Giang", "Nam Dinh", "Ha Noi", "Hung Yen", "Ha Nam"]),
            math_score=random.choice([10, 9, 8]),
            literature_score=random.choice([10, 9, 8]),
            english_score=random.choice([10, 9, 8])
        ))
    return lst


@router.get("/students/{student_id}", summary="Get students by student_id")
def get_student(student_id: str) -> StudentResponse:
    return StudentResponse(
        student_id=student_id,
        first_name=random.choice(["Nam", "An", "Hang", "Tuan", "Lam", "Ninh", "Lan"]),
        last_name=random.choice(["Nguyen", "Trinh", "Le", "Vu", "Ton"]),
        email=cast(EmailStr, "example@gmail.com"),
        date_of_birth=cast(date, "2025-12-31"),
        home_town=random.choice(["Bac Giang", "Nam Dinh", "Ha Noi", "Hung Yen", "Ha Nam"]),
        math_score=random.choice([10, 9, 8]),
        literature_score=random.choice([10, 9, 8]),
        english_score=random.choice([10, 9, 8])
    )