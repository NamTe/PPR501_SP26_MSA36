from fastapi import APIRouter, FastAPI, WebSocket
from starlette import status

router = APIRouter(
    prefix='/v1/api/students'
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def read_root():
    return {"Hello": "World"}

@router.get("/")
def read_root():
    return {"Hello": "World"}