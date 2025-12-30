from fastapi import FastAPI
from api import student_api
from contextlib import asynccontextmanager

from database.create_db_and_tables import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    # create db and table on start up
    create_db_and_tables()
    yield
    # Clean up and release the resources

app = FastAPI(lifespan=lifespan)

@app.get("/items/{item_id}")
async def read_user_item(item_id: str, needy: str):
    item = {"item_id": item_id, "needy": needy}
    return item

app.include_router(student_api.router)