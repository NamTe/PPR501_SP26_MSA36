from fastapi import FastAPI
from api import student_api
from contextlib import asynccontextmanager

from database.create_db_and_tables import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # create db and table on start up
    create_db_and_tables()
    yield
    # Clean up the ML models and release the resources

app = FastAPI(lifespan=lifespan)

app.include_router(student_api.router)