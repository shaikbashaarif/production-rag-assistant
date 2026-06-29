from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text

from app.core.config import settings
from app.api.routes import router
from app.db.database import Base, engine
from app.api.auth_routes import auth_router


# Enable pgvector first
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()

# Then create tables
Base.metadata.create_all(bind=engine)


app = FastAPI(title=settings.app_name)

origins = [origin.strip() for origin in settings.cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
app.include_router(auth_router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "RAG Freelance Assistant backend is running",
        "docs": "/docs",
        "health": "/api/health",
    }