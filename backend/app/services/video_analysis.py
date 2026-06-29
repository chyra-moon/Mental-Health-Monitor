import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote, urlparse

from fastapi import UploadFile

from app.config import settings
from app.models.user import User
from app.models.video import VideoAnalysisSession, VideoFrameEmotionRecord
from app.services import emotion as emotion_svc
from app.services.risk import NEGATIVE_EMOTIONS, evaluate_video_risk
from app.utils.json import to_jsonable

VIDEO_ROOT = Path(settings.video_dir)
VIDEO_ROOT.mkdir(parents=True, exist_ok=True)
BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
FRONTEND_PUBLIC_ROOT = PROJECT_ROOT / "frontend" / "public"

_INVALID_PATH_CHARS = re.compile(r'[\\/:*?"<>|]+')
_ALLOWED_VIDEO_EXTS = {".webm", ".mp4", ".mov", ".mkv", ".avi", ".ogv"}
_VIDEO_CONTENT_TYPE_MAP = {
    "video/webm": ".webm",
    "video/mp4": ".mp4",
    "video/quicktime": ".mov",
    "video/ogg": ".ogv",
    "video/x-matroska": ".mkv",
}
EMOTION_LABELS = {
    "happy": "开心",
    "sad": "悲伤",
    "angry": "愤怒",
    "fear": "恐惧",
    "disgust": "厌恶",
    "surprise": "惊讶",
    "neutral": "平静",
}
EMOTION_COLORS = {
    "happy": "#67C23A",
    "sad": "#409EFF",
    "angry": "#F56C6C",
    "fear": "#E6A23C",
    "disgust": "#A0522D",
    "surprise": "#9C27B0",
    "neutral": "#909399",
}


def sanitize_path_component(value: str | None, fallback: str = "student") -> str:
    text = (value or "").strip()
    if not text:
        return fallback
    text = _INVALID_PATH_CHARS.sub("_", text)
    text = re.sub(r"\s+", "_", text)
    text = text.strip("._ ")
    return text or fallback


def build_student_video_dir(student: User) -> Path:
    student_name = sanitize_path_component(student.real_name or student.username or "student")
    return VIDEO_ROOT / f"{student_name}_{student.id}"


def detect_video_extension(upload: UploadFile) -> str:
    filename_ext = Path(upload.filename or "").suffix.lower()
    if filename_ext in _ALLOWED_VIDEO_EXTS:
        return filename_ext

    content_type = (upload.content_type or "").lower()
    if content_type in _VIDEO_CONTENT_TYPE_MAP:
        return _VIDEO_CONTENT_TYPE_MAP[content_type]

    return ".webm"


def save_upload_file(upload: UploadFile, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as output_file:
        shutil.copyfileobj(upload.file, output_file)
    upload.file.seek(0)


def resolve_video_source(source: str | None) -> Path:
    if not source:
        raise ValueError("未提供视频路径")

    parsed = urlparse(source)
    if parsed.scheme in {"http", "https"}:
        raise ValueError("当前后端仅支持服务器本地视频文件，请提供本地路径或 /videos/ 下的视频")

    raw_path = unquote(parsed.path if parsed.scheme == "file" else source).strip()
    candidates: list[Path] = []
    input_path = Path(raw_path)

    if raw_path.startswith("/videos/") or raw_path.startswith("videos/"):
        candidates.append((FRONTEND_PUBLIC_ROOT / raw_path.lstrip("/")).resolve())

    if input_path.is_absolute():
        candidates.append(input_path)
    else:
        candidates.extend(
            [
                (FRONTEND_PUBLIC_ROOT / raw_path.lstrip("/")).resolve(),
                (PROJECT_ROOT / raw_path.lstrip("/")).resolve(),
                (BACKEND_ROOT / raw_path.lstrip("/")).resolve(),
                (VIDEO_ROOT / raw_path.lstrip("/")).resolve(),
            ]
        )

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            if candidate.suffix.lower() not in _ALLOWED_VIDEO_EXTS:
                raise ValueError("视频格式不支持")
            return candidate

    raise ValueError(f"视频文件不存在：{source}")


def encode_frame_to_jpeg(frame) -> bytes:
    import cv2

    ok, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
    if not ok:
        raise ValueError("视频帧编码失败")
    return encoded.tobytes()


def iter_sampled_video_frames(video_path: Path, frame_interval_ms: int = 1000, max_frames: int | None = None):
    import cv2

    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise ValueError("无法打开视频文件")

    try:
        fps = float(capture.get(cv2.CAP_PROP_FPS) or 0)
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        frame_index = 0

        if fps > 0 and frame_count > 0:
            duration_ms = int((frame_count / fps) * 1000)
            timestamp_ms = 0
            while timestamp_ms <= duration_ms:
                if max_frames is not None and frame_index >= max_frames:
                    break
                capture.set(cv2.CAP_PROP_POS_MSEC, timestamp_ms)
                ok, frame = capture.read()
                if not ok:
                    break
                yield frame_index, timestamp_ms, frame
                frame_index += 1
                timestamp_ms += frame_interval_ms
            return

        sample_every = max(int(fps * (frame_interval_ms / 1000)), 1) if fps > 0 else 25
        read_index = 0
        while True:
            if max_frames is not None and frame_index >= max_frames:
                break
            ok, frame = capture.read()
            if not ok:
                break
            if read_index % sample_every == 0:
                timestamp_ms = int((read_index / fps) * 1000) if fps > 0 else frame_index * frame_interval_ms
                yield frame_index, timestamp_ms, frame
                frame_index += 1
            read_index += 1
    finally:
        capture.release()


def analyze_video_file(
    video_path: Path,
    frame_interval_ms: int = 1000,
    max_frames: int | None = None,
) -> list[dict]:
    frame_results = []
    for frame_index, timestamp_ms, frame in iter_sampled_video_frames(video_path, frame_interval_ms, max_frames):
        try:
            image_bytes = encode_frame_to_jpeg(frame)
            result = to_jsonable(emotion_svc.analyze_face(image_bytes))
            dominant_emotion = result["dominant_emotion"]
            confidence = round(float(result["confidence"]), 4)
            emotion_scores = {
                emotion: round(float(score), 4)
                for emotion, score in result["emotion_scores"].items()
            }
            frame_status = "ok"
            error_message = None
        except ValueError as exc:
            dominant_emotion = None
            confidence = None
            emotion_scores = None
            frame_status = "no_face"
            error_message = str(exc)
        except Exception as exc:
            dominant_emotion = None
            confidence = None
            emotion_scores = None
            frame_status = "error"
            error_message = str(exc)

        frame_results.append(
            {
                "frame_index": frame_index,
                "timestamp_ms": timestamp_ms,
                "analysis_status": frame_status,
                "dominant_emotion": dominant_emotion,
                "confidence": confidence,
                "emotion_scores": emotion_scores,
                "error_message": error_message,
            }
        )

    if not frame_results:
        raise ValueError("视频中未抽取到可分析的帧")

    return frame_results


def serialize_frame_record(frame: VideoFrameEmotionRecord) -> dict:
    return {
        "id": frame.id,
        "session_id": frame.session_id,
        "student_id": frame.student_id,
        "frame_index": frame.frame_index,
        "timestamp_ms": frame.timestamp_ms,
        "analysis_status": frame.analysis_status,
        "dominant_emotion": frame.dominant_emotion,
        "confidence": float(frame.confidence) if frame.confidence is not None else None,
        "emotion_scores": to_jsonable(frame.emotion_scores) if frame.emotion_scores else None,
        "error_message": frame.error_message,
        "created_at": frame.created_at.isoformat() if frame.created_at else None,
    }


def summarize_frames(frames: Iterable[VideoFrameEmotionRecord]) -> dict:
    frame_list = list(frames)
    ok_frames = [frame for frame in frame_list if frame.analysis_status == "ok" and frame.dominant_emotion]
    analyzed_count = len(ok_frames)
    total_frames = len(frame_list)

    emotion_distribution = Counter(frame.dominant_emotion for frame in ok_frames if frame.dominant_emotion)
    average_scores = defaultdict(float)
    average_counts = defaultdict(int)
    dominant_confidence_sum = 0.0

    for frame in ok_frames:
        if frame.confidence is not None:
            dominant_confidence_sum += float(frame.confidence)
        for emotion, score in (frame.emotion_scores or {}).items():
            if score is None:
                continue
            average_scores[emotion] += float(score)
            average_counts[emotion] += 1

    dominant_emotion = None
    if emotion_distribution:
        dominant_emotion = max(emotion_distribution.items(), key=lambda item: (item[1], item[0]))[0]

    negative_count = sum(count for emotion, count in emotion_distribution.items() if emotion in NEGATIVE_EMOTIONS)
    negative_ratio = round(negative_count / analyzed_count, 4) if analyzed_count else 0.0
    dominant_confidence = round(dominant_confidence_sum / analyzed_count, 4) if analyzed_count else None

    average_emotion_scores = {
        emotion: round(average_scores[emotion] / average_counts[emotion], 4)
        for emotion in average_scores
        if average_counts[emotion]
    }

    risk_level, reason, suggestion = evaluate_video_risk(dominant_emotion, negative_ratio, analyzed_count)

    return {
        "total_frames": total_frames,
        "analyzed_frames": analyzed_count,
        "dominant_emotion": dominant_emotion,
        "emotion_distribution": dict(emotion_distribution),
        "average_emotion_scores": average_emotion_scores,
        "negative_ratio": negative_ratio,
        "dominant_confidence": dominant_confidence,
        "risk_level": risk_level,
        "reason": reason,
        "suggestion": suggestion,
    }


def _frame_time_label(frame: VideoFrameEmotionRecord) -> str:
    return f"{frame.timestamp_ms / 1000:.1f}s"


def build_visualization_payload(
    frames: Iterable[VideoFrameEmotionRecord],
    summary: dict | None = None,
) -> dict:
    frame_list = list(frames)
    summary = summary or summarize_frames(frame_list)
    valid_frames = [
        frame for frame in frame_list
        if frame.analysis_status == "ok" and frame.dominant_emotion
    ]

    x_axis = [_frame_time_label(frame) for frame in frame_list]
    valid_x_axis = [_frame_time_label(frame) for frame in valid_frames]

    timeline = [
        {
            "frame_index": frame.frame_index,
            "timestamp_ms": frame.timestamp_ms,
            "time_label": _frame_time_label(frame),
            "analysis_status": frame.analysis_status,
            "dominant_emotion": frame.dominant_emotion,
            "emotion_label": EMOTION_LABELS.get(frame.dominant_emotion or "", frame.dominant_emotion),
            "confidence": float(frame.confidence) if frame.confidence is not None else None,
            "confidence_percent": round(float(frame.confidence) * 100, 1) if frame.confidence is not None else None,
        }
        for frame in frame_list
    ]

    analyzed_frames = summary.get("analyzed_frames") or 0
    distribution = [
        {
            "emotion": emotion,
            "label": EMOTION_LABELS.get(emotion, emotion),
            "value": count,
            "percent": round(count / analyzed_frames * 100, 1) if analyzed_frames else 0,
            "color": EMOTION_COLORS.get(emotion, "#909399"),
        }
        for emotion, count in (summary.get("emotion_distribution") or {}).items()
    ]

    status_counter = Counter(frame.analysis_status for frame in frame_list)
    status_distribution = [
        {"status": status, "value": count}
        for status, count in status_counter.items()
    ]

    confidence_data = [
        round(float(frame.confidence) * 100, 1) if frame.confidence is not None else None
        for frame in valid_frames
    ]

    score_series = []
    for emotion in EMOTION_LABELS:
        score_series.append(
            {
                "emotion": emotion,
                "name": EMOTION_LABELS[emotion],
                "color": EMOTION_COLORS.get(emotion, "#909399"),
                "data": [
                    round(float((frame.emotion_scores or {}).get(emotion)) * 100, 1)
                    if (frame.emotion_scores or {}).get(emotion) is not None
                    else None
                    for frame in valid_frames
                ],
            }
        )

    return {
        "timeline": timeline,
        "emotion_distribution": distribution,
        "status_distribution": status_distribution,
        "confidence_line": {
            "x_axis": valid_x_axis,
            "series": [{"name": "主情绪置信度", "data": confidence_data}],
        },
        "emotion_score_lines": {
            "x_axis": valid_x_axis,
            "series": score_series,
        },
        "echarts": {
            "confidence_line": {
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "category", "data": valid_x_axis},
                "yAxis": {"type": "value", "min": 0, "max": 100, "name": "%"},
                "series": [{"name": "主情绪置信度", "type": "line", "smooth": True, "data": confidence_data}],
            },
            "emotion_distribution_pie": {
                "tooltip": {"trigger": "item"},
                "series": [
                    {
                        "type": "pie",
                        "radius": ["38%", "70%"],
                        "data": [
                            {
                                "name": item["label"],
                                "value": item["value"],
                                "itemStyle": {"color": item["color"]},
                            }
                            for item in distribution
                        ],
                    }
                ],
            },
            "emotion_score_lines": {
                "tooltip": {"trigger": "axis"},
                "legend": {"type": "scroll"},
                "xAxis": {"type": "category", "data": valid_x_axis},
                "yAxis": {"type": "value", "min": 0, "max": 100, "name": "%"},
                "series": [
                    {
                        "name": item["name"],
                        "type": "line",
                        "smooth": True,
                        "data": item["data"],
                        "lineStyle": {"color": item["color"]},
                        "itemStyle": {"color": item["color"]},
                    }
                    for item in score_series
                ],
            },
        },
    }


def build_session_payload(
    session: VideoAnalysisSession,
    student: User | None,
    admin: User | None,
    frames: Iterable[VideoFrameEmotionRecord] | None = None,
) -> dict:
    frame_list = list(frames or [])
    summary = summarize_frames(frame_list) if frame_list else {
        "total_frames": session.total_frames,
        "analyzed_frames": session.analyzed_frames,
        "dominant_emotion": session.dominant_emotion,
        "emotion_distribution": to_jsonable(session.emotion_distribution) or {},
        "average_emotion_scores": to_jsonable(session.average_emotion_scores) or {},
        "negative_ratio": float(session.negative_ratio) if session.negative_ratio is not None else 0.0,
        "dominant_confidence": float(session.dominant_confidence) if session.dominant_confidence is not None else None,
        "risk_level": session.risk_level,
        "reason": session.reason,
        "suggestion": session.suggestion,
    }

    return {
        "id": session.id,
        "student_id": session.student_id,
        "student_name": student.real_name if student else None,
        "student_username": student.username if student else None,
        "admin_id": session.admin_id,
        "admin_name": admin.real_name if admin else None,
        "admin_username": admin.username if admin else None,
        "frame_interval_ms": session.frame_interval_ms,
        "status": session.status,
        "video_path": session.video_path,
        "video_filename": session.video_filename,
        "video_content_type": session.video_content_type,
        "started_at": session.started_at.isoformat() if session.started_at else None,
        "ended_at": session.ended_at.isoformat() if session.ended_at else None,
        "created_at": session.created_at.isoformat() if session.created_at else None,
        "summary": summary,
        "frames": [serialize_frame_record(frame) for frame in frame_list],
        "visualization": build_visualization_payload(frame_list, summary),
    }
