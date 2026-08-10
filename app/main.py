from fastapi import FastAPI

from app.api.router import router as packages_router
from app.db import models  # noqa: F401
from app.db.database import Base, engine


app = FastAPI(title="RouteForge")

Base.metadata.create_all(bind=engine)
app.include_router(packages_router)
