"""情绪识别服务抽象层。当前使用 DeepFace，可切换其他后端。"""

import uuid
from pathlib import Path

from app.config import settings

UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 单图按顺序尝试多个 DeepFace 检测后端，摄像头采集帧的落盘回退只尝试 retinaface。
IMAGE_DETECTOR_BACKENDS = ("retinaface", "opencv", "mtcnn", "ssd")
VIDEO_FALLBACK_DETECTOR_BACKENDS = ("retinaface",)
_FACE_CASCADE = None


# 模型依赖缺失单独上抛，调用方可与无人脸等输入问题分开处理。
class EmotionModelUnavailableError(RuntimeError):
    """DeepFace 或其运行依赖不可用。"""


def analyze_face(image_bytes: bytes) -> dict:
    """分析人脸图片，返回情绪结果。

    返回格式:
    {
        "dominant_emotion": str,
        "confidence": float,
        "emotion_scores": {"happy": 0.xx, "sad": 0.xx, ...}
    }
    """
    # 单图落盘仅供 DeepFace 读取，成功或异常后都由 finally 删除临时文件。
    temp_path = None
    try:
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

    # 摄像头采集帧先以 ndarray 调用 DeepFace，失败后尝试裁取最大人脸，最后才落盘重试。
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

    # ndarray 与裁脸路径都失败后才写临时文件，退出该回退路径时统一删除。
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
    """调用 DeepFace；模型环境不可用时返回明确错误。"""
    try:
        from deepface import DeepFace
    except (ImportError, AttributeError, ModuleNotFoundError) as exc:
        raise EmotionModelUnavailableError(
            "情绪识别模型不可用，请检查 DeepFace 及其运行依赖"
        ) from exc

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

    # 所有检测后端都报告无人脸时转为业务 ValueError，其他异常保留最后一个原始错误。
    if errors and all(_is_no_face_error(e) for e in errors):
        raise ValueError("未检测到人脸，请确保图片中包含清晰的人脸")
    if errors:
        raise errors[-1]

    raise ValueError("未检测到人脸，请确保图片中包含清晰的人脸")


def _call_model_on_array(image, detector_backend: str, enforce_detection: bool) -> dict:
    try:
        from deepface import DeepFace
    except (ImportError, AttributeError, ModuleNotFoundError) as exc:
        raise EmotionModelUnavailableError(
            "情绪识别模型不可用，请检查 DeepFace 及其运行依赖"
        ) from exc

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

    # 裁脸回退遇到多人同帧时取面积最大的框，并保留部分周边区域交给 DeepFace 分类。
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

    # DeepFace 返回百分制情绪分值，系统统一除以 100 并保留四位小数。
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
