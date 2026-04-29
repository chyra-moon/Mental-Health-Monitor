import re
import shutil
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.class_model import Class
from app.models.video import VideoAnalysisSession, VideoFrameEmotionRecord
from app.models.record import RiskWarning
from app.services import emotion as emotion_svc
from app.services.risk import evaluate_video_risk
from app.utils.deps import require_role
from app.utils.json import to_jsonable

router = APIRouter(prefix="/admin/video", tags=["视频分析管理"])

VIDEO_DIR = Path(settings.video_dir)
VIDEO_DIR.mkdir(parents=True, exist_ok=True)

EXT_WHITELIST = {".mp4", ".webm", ".ogg", ".mov", ".avi", ".mkv"}

MIME_MAP = {
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".ogg": "video/ogg",
    ".mov": "video/quicktime",
    ".avi": "video/x-msvideo",
    ".mkv": "video/x-matroska",
}

NEGATIVE_EMOTIONS = {"sad", "angry", "fear", "disgust"}

EMOTION_CN = {
    "happy": "开心", "sad": "悲伤", "angry": "愤怒",
    "fear": "恐惧", "disgust": "厌恶", "surprise": "惊讶", "neutral": "平静",
}
RISK_CN = {"low": "低风险", "medium": "中风险", "high": "高风险"}

# 匹配已处理文件名: YYYY.M.D-情绪-风险.ext
ANALYZED_PATTERN = re.compile(r"^\d{4}\.\d{1,2}\.\d{1,2}-.+$")


def _get_student_folder(student_id: int, db: Session) -> Path | None:
    """根据学生 ID 找到 vedio/{班级名}/{学生名}/ 目录。"""
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student or not student.class_id:
        return None
    cls = db.get(Class, student.class_id)
    if not cls:
        return None
    if not student.real_name:
        return None
    return VIDEO_DIR / cls.name / student.real_name


def _find_unprocessed_video(folder: Path) -> Path | None:
    """在目录中找第一个未处理的视频文件。"""
    if not folder.is_dir():
        return None
    for f in sorted(folder.iterdir()):
        if f.is_file() and f.suffix.lower() in EXT_WHITELIST:
            if not ANALYZED_PATTERN.match(f.stem):
                return f
    return None


def _build_session_response(session: VideoAnalysisSession, db: Session) -> dict:
    student = db.query(User).filter(User.id == session.student_id).first()
    class_name = None
    student_name = student.real_name if student else "未知"
    if student and student.class_id:
        cls = db.get(Class, student.class_id)
        class_name = cls.name if cls else None

    def _f(v):
        return round(float(v), 4) if v is not None else None

    return {
        "id": session.id,
        "student_id": session.student_id,
        "student_name": student_name,
        "class_name": class_name,
        "video_filename": session.video_filename,
        "status": session.status,
        "total_frames": session.total_frames,
        "analyzed_frames": session.analyzed_frames,
        "dominant_emotion": session.dominant_emotion,
        "negative_ratio": _f(session.negative_ratio),
        "risk_level": session.risk_level,
        "reason": session.reason,
        "started_at": session.started_at.isoformat(),
        "ended_at": session.ended_at.isoformat() if session.ended_at else None,
    }


# ---- 端点 ----

@router.get("/check/{student_id}")
def check_video(student_id: int, user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    """检查学生是否有未处理的视频文件。"""
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学生不存在")

    folder = _get_student_folder(student_id, db)
    if not folder:
        return {
            "code": 200, "message": "ok",
            "data": {"available": False, "student_name": student.real_name or student.username, "hint": "学生尚未分配班级或未完善个人信息"},
        }

    video = _find_unprocessed_video(folder)
    if not video:
        return {
            "code": 200, "message": "ok",
            "data": {"available": False, "student_name": student.real_name or student.username, "hint": f"当前没有{student.real_name or student.username}的最新数据"},
        }

    return {
        "code": 200, "message": "ok",
        "data": {
            "available": True,
            "filename": video.name,
            "student_name": student.real_name or student.username,
            "class_name": folder.parent.name,
            "folder": str(folder),
        },
    }


@router.get("/stream")
def stream_video(
    student_id: int,
    filename: str,
    user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学生不存在")

    folder = _get_student_folder(student_id, db)
    if not folder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="无法定位学生视频目录")

    safe_filename = Path(filename).name
    file_path = folder / safe_filename
    if not file_path.is_file() or file_path.suffix.lower() not in EXT_WHITELIST:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="视频文件不存在")
    media = MIME_MAP.get(file_path.suffix.lower(), "application/octet-stream")
    return FileResponse(str(file_path), media_type=media)


@router.post("/sessions")
def create_session(
    student_id: int = Form(...),
    frame_count: int = Form(20),
    user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    if frame_count < 5 or frame_count > 60:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="帧数需在 5-60 之间")

    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学生不存在")

    # 检查是否有同学生进行中的任务
    running = db.query(VideoAnalysisSession).filter(
        VideoAnalysisSession.student_id == student_id,
        VideoAnalysisSession.status == "running",
    ).first()
    if running:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该学生有一个视频分析任务正在进行中，请等待完成后再试")

    folder = _get_student_folder(student_id, db)
    if not folder:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无法定位学生视频目录，请确认学生已分配班级并完善个人信息")

    video_path = _find_unprocessed_video(folder)
    if not video_path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"当前没有{student.real_name or student.username}的最新数据")

    ext = video_path.suffix.lower()
    session = VideoAnalysisSession(
        student_id=student_id,
        admin_id=user.id,
        total_frames=frame_count,
        video_path=str(video_path),
        video_filename=video_path.name,
        video_content_type=MIME_MAP.get(ext, "application/octet-stream"),
        status="running",
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "code": 200,
        "message": "会话创建成功",
        "data": {
            "id": session.id,
            "student_id": session.student_id,
            "video_filename": session.video_filename,
            "total_frames": session.total_frames,
            "status": session.status,
            "stream_src": f"/api/admin/video/stream?student_id={student_id}&filename={video_path.name}",
            "started_at": session.started_at.isoformat(),
        },
    }


@router.post("/sessions/{session_id}/frames")
def analyze_frame(
    session_id: int,
    file: UploadFile = File(...),
    frame_index: int = Form(...),
    timestamp_ms: int = Form(0),
    user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    session = db.query(VideoAnalysisSession).filter(VideoAnalysisSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
    if session.status != "running":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="会话已结束")

    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持 JPG 或 PNG 图片")

    image_bytes = file.file.read()

    def _save_frame(status_, dom_emo=None, conf=None, scores=None, err_msg=None):
        f = VideoFrameEmotionRecord(
            session_id=session_id,
            student_id=session.student_id,
            frame_index=frame_index,
            timestamp_ms=timestamp_ms,
            analysis_status=status_,
            dominant_emotion=dom_emo,
            confidence=conf,
            emotion_scores=scores,
            error_message=err_msg,
        )
        db.add(f)
        session.analyzed_frames += 1
        db.commit()
        db.refresh(f)
        return f

    try:
        result = to_jsonable(emotion_svc.analyze_face(image_bytes))
    except ValueError as e:
        f = _save_frame("no_face", err_msg=str(e))
        return {
            "code": 200, "message": str(e),
            "data": {"id": f.id, "frame_index": f.frame_index, "timestamp_ms": f.timestamp_ms,
                     "analysis_status": "no_face", "dominant_emotion": None,
                     "confidence": None, "emotion_scores": None, "error_message": str(e)},
        }
    except Exception as e:
        f = _save_frame("error", err_msg=str(e))
        return {
            "code": 200, "message": "帧分析异常",
            "data": {"id": f.id, "frame_index": f.frame_index, "timestamp_ms": f.timestamp_ms,
                     "analysis_status": "error", "dominant_emotion": None,
                     "confidence": None, "emotion_scores": None, "error_message": str(e)},
        }

    confidence = round(float(result["confidence"]), 4)
    emotion_scores = {e: round(float(s), 4) for e, s in result["emotion_scores"].items()}
    f = _save_frame("ok", dom_emo=result["dominant_emotion"], conf=confidence, scores=emotion_scores)

    return {
        "code": 200, "message": "帧分析完成",
        "data": {"id": f.id, "frame_index": f.frame_index, "timestamp_ms": f.timestamp_ms,
                 "analysis_status": "ok", "dominant_emotion": result["dominant_emotion"],
                 "confidence": confidence, "emotion_scores": emotion_scores},
    }


@router.post("/sessions/{session_id}/complete")
def complete_session(
    session_id: int,
    user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    session = db.query(VideoAnalysisSession).filter(VideoAnalysisSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
    if session.status != "running":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="会话已结束")

    ok_frames = (
        db.query(VideoFrameEmotionRecord)
        .filter(
            VideoFrameEmotionRecord.session_id == session_id,
            VideoFrameEmotionRecord.analysis_status == "ok",
        )
        .all()
    )

    if not ok_frames:
        session.status = "completed"
        session.analyzed_frames = 0
        session.negative_ratio = 0
        session.dominant_emotion = None
        session.emotion_distribution = {}
        session.average_emotion_scores = {}
        session.risk_level = "low"
        session.reason = "未采集到有效视频帧"
        session.suggestion = "建议重新采集或调整摄像头角度，确保人脸清晰可见。"
        session.ended_at = datetime.now()
        _rename_video(session)
        db.commit()
        db.refresh(session)
        return {
            "code": 200, "message": "会话完成（无有效帧）",
            "data": {"id": session.id, "status": "completed", "total_frames": session.total_frames,
                     "analyzed_frames": 0, "dominant_emotion": None, "negative_ratio": 0,
                     "risk_level": "low", "reason": session.reason, "suggestion": session.suggestion,
                     "emotion_distribution": {}, "average_emotion_scores": {},
                     "video_filename": session.video_filename,
                     "ended_at": session.ended_at.isoformat()},
        }

    from collections import Counter
    emotion_counts = Counter(f.dominant_emotion for f in ok_frames)
    dominant_emotion = emotion_counts.most_common(1)[0][0]

    dom_confidences = [float(f.confidence) for f in ok_frames if f.dominant_emotion == dominant_emotion]
    dominant_confidence = round(sum(dom_confidences) / len(dom_confidences), 4)

    negative_count = sum(1 for f in ok_frames if f.dominant_emotion in NEGATIVE_EMOTIONS)
    negative_ratio = round(negative_count / len(ok_frames), 4)

    emotion_distribution = dict(emotion_counts)

    score_sums = {}
    score_counts = {}
    for f in ok_frames:
        if f.emotion_scores:
            for emo, val in f.emotion_scores.items():
                score_sums[emo] = score_sums.get(emo, 0) + float(val)
                score_counts[emo] = score_counts.get(emo, 0) + 1
    average_emotion_scores = {e: round(score_sums[e] / score_counts[e], 4) for e in score_sums}

    risk_level, reason, suggestion = evaluate_video_risk(dominant_emotion, negative_ratio, len(ok_frames))

    session.status = "completed"
    session.analyzed_frames = len(ok_frames)
    session.dominant_emotion = dominant_emotion
    session.dominant_confidence = dominant_confidence
    session.negative_ratio = negative_ratio
    session.emotion_distribution = emotion_distribution
    session.average_emotion_scores = average_emotion_scores
    session.risk_level = risk_level
    session.reason = reason
    session.suggestion = suggestion
    session.ended_at = datetime.now()

    if risk_level in ("medium", "high"):
        warning = RiskWarning(
            user_id=session.student_id,
            warning_level=risk_level,
            reason=f"[视频分析] {reason}",
            suggestion=suggestion,
        )
        db.add(warning)

    # 重命名视频文件
    _rename_video(session)

    db.commit()
    db.refresh(session)

    return {
        "code": 200, "message": "分析完成",
        "data": {
            "id": session.id, "status": session.status,
            "total_frames": session.total_frames, "analyzed_frames": session.analyzed_frames,
            "dominant_emotion": dominant_emotion, "dominant_confidence": dominant_confidence,
            "negative_ratio": negative_ratio, "emotion_distribution": emotion_distribution,
            "average_emotion_scores": average_emotion_scores,
            "risk_level": risk_level, "reason": reason, "suggestion": suggestion,
            "video_filename": session.video_filename,
            "ended_at": session.ended_at.isoformat(),
        },
    }


def _format_file_date(value: datetime | None = None) -> str:
    value = value or datetime.now()
    return f"{value.year}.{value.month}.{value.day}"


def _unique_path(path: Path) -> Path:
    if not path.exists():
        return path

    index = 2
    while True:
        candidate = path.with_name(f"{path.stem}-{index}{path.suffix}")
        if not candidate.exists():
            return candidate
        index += 1


def _rename_video(session: VideoAnalysisSession):
    """分析完成后将视频重命名为 日期-情绪-风险等级.ext 的留存文件格式。"""
    if not session.video_path:
        return
    old = Path(session.video_path)
    if not old.is_file():
        return

    today = _format_file_date(session.ended_at)
    emo_cn = EMOTION_CN.get(session.dominant_emotion, session.dominant_emotion or "未知")
    risk_cn = RISK_CN.get(session.risk_level, session.risk_level or "低风险")
    new_name = f"{today}-{emo_cn}-{risk_cn}{old.suffix}"
    new_path = _unique_path(old.parent / new_name)

    try:
        shutil.move(str(old), str(new_path))
        session.video_path = str(new_path)
        session.video_filename = new_path.name
    except OSError:
        pass  # 重命名失败不影响分析结果


@router.get("/sessions")
def list_sessions(
    student_id: int | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    q = db.query(VideoAnalysisSession)
    if student_id:
        q = q.filter(VideoAnalysisSession.student_id == student_id)
    if status:
        q = q.filter(VideoAnalysisSession.status == status)

    total = q.count()
    sessions = q.order_by(desc(VideoAnalysisSession.started_at)).offset(offset).limit(limit).all()

    return {
        "code": 200, "message": "ok",
        "data": {"total": total, "items": [_build_session_response(s, db) for s in sessions]},
    }


@router.get("/sessions/{session_id}")
def get_session_detail(
    session_id: int,
    user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    session = db.query(VideoAnalysisSession).filter(VideoAnalysisSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    stu = db.query(User).filter(User.id == session.student_id).first()
    class_name = None
    if stu and stu.class_id:
        cls = db.get(Class, stu.class_id)
        class_name = cls.name if cls else None

    frames = (
        db.query(VideoFrameEmotionRecord)
        .filter(VideoFrameEmotionRecord.session_id == session_id)
        .order_by(VideoFrameEmotionRecord.frame_index)
        .all()
    )

    def _f(v):
        return round(float(v), 4) if v is not None else None

    return {
        "code": 200, "message": "ok",
        "data": {
            "session": {
                "id": session.id,
                "student_id": session.student_id,
                "student_name": stu.real_name if stu else "未知",
                "class_name": class_name,
                "admin_id": session.admin_id,
                "video_filename": session.video_filename,
                "status": session.status,
                "total_frames": session.total_frames,
                "analyzed_frames": session.analyzed_frames,
                "dominant_emotion": session.dominant_emotion,
                "dominant_confidence": _f(session.dominant_confidence),
                "negative_ratio": _f(session.negative_ratio),
                "emotion_distribution": session.emotion_distribution,
                "average_emotion_scores": session.average_emotion_scores,
                "risk_level": session.risk_level,
                "reason": session.reason,
                "suggestion": session.suggestion,
                "started_at": session.started_at.isoformat(),
                "ended_at": session.ended_at.isoformat() if session.ended_at else None,
            },
            "frames": [
                {
                    "id": f.id, "frame_index": f.frame_index, "timestamp_ms": f.timestamp_ms,
                    "analysis_status": f.analysis_status, "dominant_emotion": f.dominant_emotion,
                    "confidence": _f(f.confidence), "emotion_scores": f.emotion_scores,
                    "error_message": f.error_message,
                }
                for f in frames
            ],
        },
    }
