# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.core.config import settings
# from app.api.routes import router
# from app.db.database import init_db

# app = FastAPI(title=settings.app_name)

# @app.on_event("startup")
# def on_startup():
#     init_db()

# origins = [origin.strip() for origin in settings.cors_origins.split(",")]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.get("/")
# def root():
#     return {
#         "message": "RAG Freelance Assistant backend is running",
#         "docs": "/docs",
#         "health": "/api/health"
#     }


# app.include_router(router, prefix="/api")


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import router
from app.db.database import Base, engine


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


@app.get("/")
def root():
    return {
        "message": "RAG Freelance Assistant backend is running",
        "docs": "/docs",
        "health": "/api/health",
    }