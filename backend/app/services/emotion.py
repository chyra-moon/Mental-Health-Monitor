"""情绪识别服务抽象层。当前使用 DeepFace，可切换其他后端。"""

import os
import uuid
from pathlib import Path

from app.config import settings

UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def analyze_face(image_bytes: bytes) -> dict:
    """分析人脸图片，返回情绪结果。

    返回格式:
    {
        "dominant_emotion": str,
        "confidence": float,
        "emotion_scores": {"happy": 0.xx, "sad": 0.xx, ...}
    }
    """
    temp_path = None
    try:
        # 保存临时文件
        ext = _detect_ext(image_bytes)
        filename = f"{uuid.uuid4().hex}{ext}"
        temp_path = UPLOAD_DIR / filename
        temp_path.write_bytes(image_bytes)

        return _call_model(str(temp_path))
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


def _detect_ext(data: bytes) -> str:
    if data.startswith(b"\xff\xd8"):
        return ".jpg"
    if data.startswith(b"\x89PNG"):
        return ".png"
    return ".jpg"


def _call_model(image_path: str) -> dict:
    """实际调用模型。如 DeepFace 不可用，返回模拟数据保证开发流程。"""
    try:
        from deepface import DeepFace

        result = DeepFace.analyze(img_path=image_path, actions=["emotion"], enforce_detection=True)

        if isinstance(result, list):
            result = result[0]

        emotions = result.get("emotion", {})
        dominant = max(emotions, key=emotions.get)
        return {
            "dominant_emotion": dominant,
            "confidence": round(float(emotions[dominant]) / 100, 4),
            "emotion_scores": {k: round(float(v) / 100, 4) for k, v in emotions.items()},
        }
    except (ImportError, AttributeError, ModuleNotFoundError) as e:
        if "face" in str(e).lower():
            raise ValueError("未检测到人脸，请确保图片中包含清晰的人脸")
        return _mock_result()
    except Exception as e:
        err_msg = str(e).lower()
        if "face" in err_msg and "detect" in err_msg:
            raise ValueError("未检测到人脸，请确保图片中包含清晰的人脸")
        if "exception while loading" in err_msg:
            raise ValueError("图片加载失败，请确认上传的是有效的图片文件")
        raise


def _mock_result() -> dict:
    """DeepFace 不可用时返回模拟数据，保证开发进度不阻塞。"""
    return {
        "dominant_emotion": "neutral",
        "confidence": 0.85,
        "emotion_scores": {
            "angry": 0.01, "disgust": 0.01, "fear": 0.01,
            "happy": 0.05, "sad": 0.05, "surprise": 0.02,
            "neutral": 0.85,
        },
    }
