from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.record import EmotionRecord
from app.utils.deps import get_current_user, require_role

router = APIRouter(prefix="/records", tags=["记录"])


@router.get("/my")
def my_records(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = (
        db.query(EmotionRecord)
        .filter(EmotionRecord.user_id == user.id)
        .order_by(EmotionRecord.created_at.desc())
        .limit(50)
        .all()
    )
    return {
        "code": 200,
        "message": "ok",
        "data": [
            {
                "id": r.id,
                "dominant_emotion": r.dominant_emotion,
                "confidence": float(r.confidence) if r.confidence else None,
                "risk_level": r.risk_level,
                "created_at": r.created_at.isoformat(),
            }
            for r in records
        ],
    }


@router.get("/admin/all")
def all_records(
    user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    records = (
        db.query(EmotionRecord)
        .order_by(EmotionRecord.created_at.desc())
        .limit(200)
        .all()
    )

    user_ids = list(set(r.user_id for r in records))
    users = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()}

    data = []
    for r in records:
        u = users.get(r.user_id)
        data.append({
            "id": r.id,
            "user_id": r.user_id,
            "username": u.username if u else None,
            "real_name": u.real_name if u else None,
            "dominant_emotion": r.dominant_emotion,
            "confidence": float(r.confidence) if r.confidence else None,
            "risk_level": r.risk_level,
            "created_at": r.created_at.isoformat(),
        })

    return {"code": 200, "message": "ok", "data": data}
