from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from api import student_api
from contextlib import asynccontextmanager

from database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    # create db and table on start up
    create_db_and_tables()
    yield
    # Clean up and release the resources

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(lifespan=lifespan)
app.include_router(student_api.router)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def serve_frontend() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
