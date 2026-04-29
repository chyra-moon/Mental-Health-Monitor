from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.record import EmotionRecord
from app.models.video import VideoAnalysisSession
from app.utils.deps import get_current_user, require_role

router = APIRouter(prefix="/records", tags=["记录"])


def _f(value):
    return float(value) if value is not None else None


def _image_record_payload(record: EmotionRecord, student: User | None = None) -> dict:
    payload = {
        "id": f"image-{record.id}",
        "raw_id": record.id,
        "source_type": "image",
        "source_label": "图片识别",
        "user_id": record.user_id,
        "dominant_emotion": record.dominant_emotion,
        "confidence": _f(record.confidence),
        "emotion_scores": record.emotion_scores,
        "risk_level": record.risk_level,
        "reason": None,
        "suggestion": record.suggestion,
        "negative_ratio": None,
        "analyzed_frames": None,
        "total_frames": None,
        "video_filename": None,
        "created_at": record.created_at.isoformat(),
    }
    if student:
        payload.update({
            "username": student.username,
            "real_name": student.real_name,
        })
    return payload


def _video_record_payload(session: VideoAnalysisSession, student: User | None = None) -> dict:
    created_at = session.ended_at or session.started_at or session.created_at
    payload = {
        "id": f"video-{session.id}",
        "raw_id": session.id,
        "source_type": "video",
        "source_label": "视频分析",
        "user_id": session.student_id,
        "dominant_emotion": session.dominant_emotion,
        "confidence": _f(session.dominant_confidence),
        "emotion_scores": session.average_emotion_scores,
        "risk_level": session.risk_level,
        "reason": session.reason,
        "suggestion": session.suggestion,
        "negative_ratio": _f(session.negative_ratio),
        "analyzed_frames": session.analyzed_frames,
        "total_frames": session.total_frames,
        "video_filename": session.video_filename,
        "created_at": created_at.isoformat(),
    }
    if student:
        payload.update({
            "username": student.username,
            "real_name": student.real_name,
        })
    return payload


@router.get("/my")
def my_records(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    image_records = (
        db.query(EmotionRecord)
        .filter(EmotionRecord.user_id == user.id)
        .order_by(EmotionRecord.created_at.desc())
        .limit(50)
        .all()
    )
    video_records = (
        db.query(VideoAnalysisSession)
        .filter(
            VideoAnalysisSession.student_id == user.id,
            VideoAnalysisSession.status == "completed",
        )
        .order_by(VideoAnalysisSession.ended_at.desc())
        .limit(50)
        .all()
    )

    items = [_image_record_payload(r) for r in image_records]
    items.extend(_video_record_payload(v) for v in video_records)
    items.sort(key=lambda item: item["created_at"], reverse=True)

    return {
        "code": 200,
        "message": "ok",
        "data": items[:50],
    }


@router.get("/admin/all")
def all_records(
    user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    image_records = (
        db.query(EmotionRecord)
        .order_by(EmotionRecord.created_at.desc())
        .limit(200)
        .all()
    )
    video_records = (
        db.query(VideoAnalysisSession)
        .filter(VideoAnalysisSession.status == "completed")
        .order_by(VideoAnalysisSession.ended_at.desc())
        .limit(200)
        .all()
    )

    user_ids = list({r.user_id for r in image_records} | {v.student_id for v in video_records})
    users = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()}

    data = []
    for r in image_records:
        data.append(_image_record_payload(r, users.get(r.user_id)))
    for v in video_records:
        data.append(_video_record_payload(v, users.get(v.student_id)))

    data.sort(key=lambda item: item["created_at"], reverse=True)

    return {"code": 200, "message": "ok", "data": data[:200]}
