"""情绪识别服务抽象层。当前使用 DeepFace，可切换其他后端。"""

import uuid
from pathlib import Path

from app.config import settings

UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 图片单次识别优先准确；视频逐帧识别会走单独的快速裁脸路径。
IMAGE_DETECTOR_BACKENDS = ("retinaface", "opencv", "mtcnn", "ssd")
VIDEO_FALLBACK_DETECTOR_BACKENDS = ("retinaface",)
_FACE_CASCADE = None


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

        return _call_model(str(temp_path), IMAGE_DETECTOR_BACKENDS)
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


def analyze_video_frame(image_bytes: bytes) -> dict:
    """分析视频帧。

    视频优先使用 DeepFace 的 opencv 检测器做对齐后分类。
    直接手动裁脸再跳过检测虽然更快，但对齐不稳定，容易把笑脸误判为恐惧。
    opencv 仍然足够快；失败时再回退到裁脸和 retinaface。
    """
    try:
        frame = _decode_image(image_bytes)
    except ValueError:
        raise
    except Exception:
        frame = None

    if frame is not None:
        try:
            return _call_model_on_array(frame, detector_backend="opencv", enforce_detection=True)
        except Exception as e:
            if _is_image_load_error(e):
                raise ValueError("图片加载失败，请确认上传的是有效的图片文件")

        try:
            face = _crop_largest_face(frame)
            if face is not None:
                return _call_model_on_array(face, detector_backend="skip", enforce_detection=False)
        except Exception:
            pass

    temp_path = None
    try:
        ext = _detect_ext(image_bytes)
        filename = f"{uuid.uuid4().hex}{ext}"
        temp_path = UPLOAD_DIR / filename
        temp_path.write_bytes(image_bytes)
        return _call_model(str(temp_path), VIDEO_FALLBACK_DETECTOR_BACKENDS)
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


def warm_up_emotion_model() -> None:
    """后台预热 DeepFace 情绪模型，避免首帧分析承担 TensorFlow 加载耗时。"""
    try:
        from deepface import DeepFace

        DeepFace.build_model("Emotion", task="facial_attribute")
    except Exception:
        pass


def _detect_ext(data: bytes) -> str:
    if data.startswith(b"\xff\xd8"):
        return ".jpg"
    if data.startswith(b"\x89PNG"):
        return ".png"
    return ".jpg"


def _call_model(image_path: str, detector_backends: tuple[str, ...]) -> dict:
    """实际调用模型。如 DeepFace 不可用，返回模拟数据保证开发流程。"""
    try:
        from deepface import DeepFace
    except (ImportError, AttributeError, ModuleNotFoundError) as e:
        if "face" in str(e).lower():
            raise ValueError("未检测到人脸，请确保图片中包含清晰的人脸")
        return _mock_result()

    errors = []
    for backend in detector_backends:
        try:
            result = DeepFace.analyze(
                img_path=image_path,
                actions=["emotion"],
                detector_backend=backend,
                enforce_detection=True,
            )
            return _normalize_deepface_result(result)
        except Exception as e:
            errors.append(e)
            if _is_image_load_error(e):
                raise ValueError("图片加载失败，请确认上传的是有效的图片文件")

    if errors and all(_is_no_face_error(e) for e in errors):
        raise ValueError("未检测到人脸，请确保图片中包含清晰的人脸")
    if errors:
        raise errors[-1]

    raise ValueError("未检测到人脸，请确保图片中包含清晰的人脸")


def _call_model_on_array(image, detector_backend: str, enforce_detection: bool) -> dict:
    try:
        from deepface import DeepFace
    except (ImportError, AttributeError, ModuleNotFoundError):
        return _mock_result()

    result = DeepFace.analyze(
        img_path=image,
        actions=["emotion"],
        detector_backend=detector_backend,
        enforce_detection=enforce_detection,
        align=True,
    )
    return _normalize_deepface_result(result)


def _decode_image(image_bytes: bytes):
    import cv2
    import numpy as np

    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("图片加载失败，请确认上传的是有效的图片文件")
    return frame


def _get_face_cascade():
    global _FACE_CASCADE
    if _FACE_CASCADE is not None:
        return _FACE_CASCADE

    import cv2

    cascade_path = str(Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml")
    _FACE_CASCADE = cv2.CascadeClassifier(cascade_path)
    return _FACE_CASCADE


def _crop_largest_face(frame):
    import cv2

    cascade = _get_face_cascade()
    if cascade.empty():
        return None

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(gray, scaleFactor=1.08, minNeighbors=4, minSize=(36, 36))
    if len(faces) == 0:
        return None

    x, y, w, h = max(faces, key=lambda box: box[2] * box[3])
    pad_x = int(w * 0.35)
    pad_y = int(h * 0.45)
    height, width = frame.shape[:2]
    x1 = max(0, x - pad_x)
    y1 = max(0, y - pad_y)
    x2 = min(width, x + w + pad_x)
    y2 = min(height, y + h + pad_y)
    if x2 <= x1 or y2 <= y1:
        return None
    return frame[y1:y2, x1:x2]


def _normalize_deepface_result(result) -> dict:
    if isinstance(result, list):
        result = result[0]

    emotions = result.get("emotion", {})
    dominant = max(emotions, key=emotions.get)
    return {
        "dominant_emotion": dominant,
        "confidence": round(float(emotions[dominant]) / 100, 4),
        "emotion_scores": {k: round(float(v) / 100, 4) for k, v in emotions.items()},
    }


def _is_no_face_error(error: Exception) -> bool:
    msg = str(error).lower()
    return (
        "face" in msg
        and (
            "detect" in msg
            or "could not be detected" in msg
            or "enforce_detection" in msg
        )
    )


def _is_image_load_error(error: Exception) -> bool:
    return "exception while loading" in str(error).lower()


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
