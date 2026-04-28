from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.record import QuestionnaireRecord
from app.services.questionnaire import QUESTIONS, OPTIONS
from app.services.risk import evaluate_risk
from app.utils.deps import get_current_user

router = APIRouter(prefix="/questionnaire", tags=["问卷"])


@router.get("/questions")
def get_questions():
    return {"code": 200, "message": "ok", "data": {"questions": QUESTIONS, "options": OPTIONS}}


@router.post("/submit")
def submit(answers: list[int], user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if len(answers) != len(QUESTIONS):
        return {"code": 400, "message": f"需要回答 {len(QUESTIONS)} 道题", "data": None}

    total_score = sum(answers)
    if any(v < 0 or v > 3 for v in answers):
        return {"code": 400, "message": "每题分数必须在 0-3 之间", "data": None}

    # 获取最近一次情绪记录
    from app.models.record import EmotionRecord
    latest_emotion = (
        db.query(EmotionRecord)
        .filter(EmotionRecord.user_id == user.id)
        .order_by(EmotionRecord.created_at.desc())
        .first()
    )
    dominant = latest_emotion.dominant_emotion if latest_emotion else "neutral"

    risk_level, reason, suggestion = evaluate_risk(user.id, dominant, total_score, db)

    qr = QuestionnaireRecord(
        user_id=user.id,
        total_score=total_score,
        answers=answers,
        risk_level=risk_level,
    )
    db.add(qr)

    if risk_level in ("medium", "high"):
        from app.models.record import RiskWarning
        warning = RiskWarning(
            user_id=user.id,
            warning_level=risk_level,
            reason=reason,
            suggestion=suggestion,
        )
        db.add(warning)

    db.commit()

    return {
        "code": 200,
        "message": "提交成功",
        "data": {"total_score": total_score, "risk_level": risk_level, "suggestion": suggestion},
    }
