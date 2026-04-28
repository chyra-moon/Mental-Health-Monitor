from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.user import User
from app.models.record import EmotionRecord, RiskWarning
from app.utils.deps import get_current_user, require_role

router = APIRouter(prefix="/stats", tags=["统计"])


@router.get("/student/trend")
def student_trend(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = (
        db.query(
            func.date(EmotionRecord.created_at).label("date"),
            EmotionRecord.dominant_emotion,
            func.count().label("count"),
        )
        .filter(EmotionRecord.user_id == user.id)
        .group_by("date", EmotionRecord.dominant_emotion)
        .order_by("date")
        .limit(30)
        .all()
    )
    return {"code": 200, "message": "ok", "data": [{"date": str(r.date), "emotion": r.dominant_emotion, "count": r.count} for r in records]}


@router.get("/admin/overview")
def admin_overview(
    user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    student_count = db.query(User).filter(User.role == "student").count()
    today_count = (
        db.query(EmotionRecord)
        .filter(func.date(EmotionRecord.created_at) == func.current_date())
        .count()
    )
    high_risk = (
        db.query(RiskWarning)
        .filter(RiskWarning.warning_level.in_(["medium", "high"]), RiskWarning.status == "pending")
        .count()
    )
    return {
        "code": 200,
        "message": "ok",
        "data": {
            "student_count": student_count,
            "today_records": today_count,
            "pending_warnings": high_risk,
        },
    }


@router.get("/admin/emotion-distribution")
def emotion_distribution(
    user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(EmotionRecord.dominant_emotion, func.count().label("count"))
        .group_by(EmotionRecord.dominant_emotion)
        .all()
    )
    return {"code": 200, "message": "ok", "data": [{"emotion": r.dominant_emotion, "count": r.count} for r in rows]}


@router.get("/admin/risk-trend")
def risk_trend(
    user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(func.date(RiskWarning.created_at).label("date"), RiskWarning.warning_level, func.count().label("count"))
        .group_by("date", RiskWarning.warning_level)
        .order_by("date")
        .limit(30)
        .all()
    )
    return {"code": 200, "message": "ok", "data": [{"date": str(r.date), "level": r.warning_level, "count": r.count} for r in rows]}
