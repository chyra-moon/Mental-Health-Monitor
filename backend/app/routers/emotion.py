from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.record import EmotionRecord, RiskWarning
from app.services import emotion as emotion_svc
from app.services.risk import evaluate_risk
from app.utils.deps import get_current_user
from app.utils.json import to_jsonable

router = APIRouter(prefix="/emotion", tags=["情绪识别"])


@router.post("/analyze")
def analyze(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持 JPG 或 PNG 图片")

    image_bytes = file.file.read()

    # 模型环境故障和无人脸等输入问题分开处理，两者都不会写入情绪记录。
    try:
        result = to_jsonable(emotion_svc.analyze_face(image_bytes))
    except emotion_svc.EmotionModelUnavailableError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)) from e
    except ValueError as e:
        return {"code": 200, "message": str(e), "data": None}

    result["confidence"] = round(float(result["confidence"]), 4)
    result["emotion_scores"] = {
        emotion: round(float(score), 4)
        for emotion, score in result["emotion_scores"].items()
    }

    risk_level, reason, suggestion = evaluate_risk(
        user.id, result["dominant_emotion"], questionnaire_score=None, db=db
    )

    record = EmotionRecord(
        user_id=user.id,
        dominant_emotion=result["dominant_emotion"],
        confidence=result["confidence"],
        emotion_scores=result["emotion_scores"],
        risk_level=risk_level,
        suggestion=suggestion,
    )
    db.add(record)

    # medium/high 的识别记录与对应预警在同一事务中提交。
    if risk_level in ("medium", "high"):
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
        "message": "识别完成",
        "data": {
            "id": record.id,
            "dominant_emotion": result["dominant_emotion"],
            "confidence": float(result["confidence"]),
            "emotion_scores": result["emotion_scores"],
            "risk_level": risk_level,
            "suggestion": suggestion,
            "created_at": record.created_at.isoformat(),
        },
    }
