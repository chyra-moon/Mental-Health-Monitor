from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import app.models  # noqa: F401

from app.config import settings
from app.database import Base, engine

app = FastAPI(title="Mental Health Monitor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=200,
        content={"code": exc.status_code, "message": exc.detail, "data": None},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    first_error = exc.errors()[0] if exc.errors() else {}
    message = first_error.get("msg", "请求参数错误")
    return JSONResponse(
        status_code=200,
        content={"code": 400, "message": message, "data": None},
    )


@app.exception_handler(Exception)
async def global_exception(request: Request, exc: Exception):
    status_code = getattr(exc, "status_code", 500)
    detail = getattr(exc, "detail", None) or str(exc)
    return JSONResponse(
        status_code=200,
        content={"code": status_code, "message": detail, "data": None},
    )


@app.get("/api/health")
def health_check():
    return {"code": 200, "message": "ok", "data": None}


@app.on_event("startup")
def ensure_database_tables():
    Base.metadata.create_all(bind=engine)
    _init_default_data()


def _init_default_data():
    """初始化默认班级等数据。"""
    from app.database import SessionLocal
    from app.models.class_model import Class
    db = SessionLocal()
    try:
        if not db.query(Class).filter(Class.name == "一班").first():
            db.add(Class(name="一班"))
            db.commit()
    finally:
        db.close()


from app.routers import auth, emotion, questionnaire, warning, stats, records, users, classes, admin_video_analysis

app.include_router(auth.router, prefix="/api")
app.include_router(emotion.router, prefix="/api")
app.include_router(questionnaire.router, prefix="/api")
app.include_router(warning.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(records.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(admin_video_analysis.router, prefix="/api")
app.include_router(classes.router, prefix="/api")
app.include_router(classes.admin_router, prefix="/api")
