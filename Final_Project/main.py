from fastapi import FastAPI
from api import student_api
from contextlib import asynccontextmanager

from database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    # create db and table on start up
    create_db_and_tables()
    yield
    # Clean up and release the resources

app = FastAPI(lifespan=lifespan)
app.include_router(student_api.router)