import csv
import io
import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
from starlette import status

from database import get_session
from database.models.student import Student
from schemas import StudentRequest, StudentResponse, ImportErrorDetails, StudentImportResponse
from util import normalize_csv_row

STUDENT_UUID_LEN = 6

router = APIRouter(
    prefix='/v1/api'
)

SessionDep = Annotated[Session, Depends(get_session)]
logger = logging.getLogger('uvicorn.error')


@router.post("/students", status_code=status.HTTP_201_CREATED, summary="Create a new student")
def create_student(
        payload: StudentRequest,
        session: SessionDep) -> StudentResponse:
    try:
        logger.info(f"Creating the Student {payload.first_name} {payload.last_name}")

        student_id = f"MSA36HN{str(uuid.uuid4())[:STUDENT_UUID_LEN]}"
        student = Student(student_id=student_id, **payload.model_dump())

        logger.debug(student)

        session.add(student)
        session.commit()
        session.refresh(student)

        logger.info("Student created")
        return StudentResponse.model_validate(student)
    except Exception as err:
        logger.error(err)
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong")


@router.put("/students/{student_id}", summary="Update a student")
def update_student(
        student_id: str,
        payload: StudentRequest,
        session: SessionDep) -> StudentResponse:
    try:
        logger.info(f"Updating the Student {payload.first_name} {payload.last_name}")
        student = session.get(Student, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        student_data = payload.model_dump(exclude_unset=True)
        student.sqlmodel_update(student_data)
        session.add(student)
        session.commit()
        session.refresh(student)

        logger.info("Student updated")

        return StudentResponse.model_validate(student)
    except HTTPException:
        logger.info(f"Student {payload.first_name} {payload.last_name} not found")
        raise
    except Exception as err:
        logger.error(err)
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong")


@router.delete("/students/{student_id}", summary="Delete a student", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
        student_id: str,
        session: SessionDep) -> None:
    try:
        logger.info(f"Deleting the Student {student_id}")
        student = session.get(Student, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        session.delete(student)
        session.commit()
        logger.info("Student deleted")
    except HTTPException:
        logger.info(f"Student {student_id} not found")
        raise
    except Exception as err:
        logger.error(err)
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong")


@router.get("/students", summary="Get all students")
def get_students(session: SessionDep) -> list[StudentResponse]:
    logger.info("Get all students")
    students = session.exec(select(Student)).all()
    return [StudentResponse.model_validate(student) for student in students]


@router.get("/students/{student_id}", summary="Get student by student_id")
def get_student(
        student_id: str,
        session: SessionDep) -> StudentResponse:
    logger.info(f"Get student by student_id: {student_id}")
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return StudentResponse.model_validate(student)


@router.post(
    "/students/import/csv",
    status_code=status.HTTP_201_CREATED,
    summary="Import students from CSV"
)
def import_students_from_csv(
        file: Annotated[UploadFile, File(description="CSV file contain students information")],
        session: SessionDep) -> StudentImportResponse:
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported"
        )

    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))

    required_fields = set(StudentRequest.model_fields.keys())
    if set(reader.fieldnames or []) != required_fields:
        raise HTTPException(
            status_code=400,
            detail=f"CSV header must be exactly: {required_fields}"
        )

    success = list()
    failed = list()

    for index, row in enumerate(reader, start=1):
        try:
            normalized = normalize_csv_row(row)
            logger.info(f"Student {normalized}")
            payload = StudentRequest.model_validate(normalized)

            student = Student(
                student_id=f"MSA36HN{str(uuid.uuid4())[:STUDENT_UUID_LEN]}",
                **payload.model_dump()
            )
            logger.info(f"Mapped to Student {student}")
            session.add(student)
            session.commit()
            session.refresh(student)

            success.append(
                StudentResponse.model_validate(student)
            )

        except Exception as err:
            session.rollback()
            logger.error(f"CSV import error at row {index}: {err}")

            failed.append(ImportErrorDetails(
                row=index,
                data=row,
                error=str(err)
            ))

    return StudentImportResponse(
        total=len(success) + len(failed),
        success_count=len(success),
        failed_count=len(failed),
        success=success,
        failed=failed
    )
