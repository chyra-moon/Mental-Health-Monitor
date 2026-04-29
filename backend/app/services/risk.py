from sqlalchemy.orm import Session

from app.models.record import EmotionRecord
from app.models.user import User

NEGATIVE_EMOTIONS = {"sad", "angry", "fear", "disgust"}
EMOTION_LABELS = {
    "happy": "开心",
    "sad": "悲伤",
    "angry": "愤怒",
    "fear": "恐惧",
    "disgust": "厌恶",
    "surprise": "惊讶",
    "neutral": "平静",
}

SUGGESTIONS = {
    "low": "当前状态较为稳定，建议保持规律作息、适度运动，并继续观察。",
    "medium": "建议主动放松压力，和朋友或老师沟通，必要时寻求心理支持。",
    "high": "建议管理员重点关注，并建议学生及时寻求专业心理老师协助。",
}


def _emotion_label(value: str | None) -> str:
    return EMOTION_LABELS.get(value or "", value or "未知")


def evaluate_risk(user_id: int, dominant_emotion: str, questionnaire_score: int | None, db: Session) -> tuple:
    """基于规则评估单次图像情绪风险，返回 (risk_level, reason, suggestion)。"""
    score = 0
    reasons = []

    if dominant_emotion in NEGATIVE_EMOTIONS:
        score += 1
        reasons.append(f"本次识别为负面情绪（{_emotion_label(dominant_emotion)}）")

    week_negatives = (
        db.query(EmotionRecord)
        .filter(
            EmotionRecord.user_id == user_id,
            EmotionRecord.dominant_emotion.in_(NEGATIVE_EMOTIONS),
        )
        .count()
    )
    if week_negatives >= 3:
        score += 2
        reasons.append(f"近一段时间出现多次负面情绪（{week_negatives}次）")
    elif week_negatives >= 1:
        score += 1
        reasons.append(f"近一段时间出现负面情绪（{week_negatives}次）")

    if questionnaire_score is not None and questionnaire_score >= 16:
        score += 2
        reasons.append(f"心理问卷得分偏高（{questionnaire_score}分）")
    elif questionnaire_score is not None and questionnaire_score >= 10:
        score += 1
        reasons.append(f"心理问卷得分偏高（{questionnaire_score}分）")

    if score >= 4:
        level = "high"
    elif score >= 2:
        level = "medium"
    else:
        level = "low"

    return level, "; ".join(reasons) if reasons else "常规监测", SUGGESTIONS[level]


def evaluate_video_risk(
    dominant_emotion: str | None,
    negative_ratio: float,
    analyzed_frames: int,
    average_emotion_scores: dict | None = None,
) -> tuple:
    """基于视频会话汇总结果评估风险。"""
    if analyzed_frames <= 0:
        return "low", "未采集到有效视频帧", SUGGESTIONS["low"]

    score = 0
    reasons = []
    average_emotion_scores = average_emotion_scores or {}
    negative_score_avg = sum(float(average_emotion_scores.get(e, 0) or 0) for e in NEGATIVE_EMOTIONS)
    sad_score_avg = float(average_emotion_scores.get("sad", 0) or 0)

    if dominant_emotion in NEGATIVE_EMOTIONS:
        score += 1
        reasons.append(f"汇总主要情绪为负面情绪（{_emotion_label(dominant_emotion)}）")

    if negative_ratio >= 0.6:
        score += 2
        reasons.append(f"负面情绪占比达到 {negative_ratio:.0%}")
    elif negative_ratio >= 0.3:
        score += 1
        reasons.append(f"负面情绪占比达到 {negative_ratio:.0%}")

    if analyzed_frames >= 5 and negative_ratio >= 0.5:
        score += 1
        reasons.append("连续多帧出现较多负面情绪")

    if negative_score_avg >= 0.55:
        score += 2
        reasons.append(f"平均负面情绪分数达到 {negative_score_avg:.0%}")
    elif negative_score_avg >= 0.35:
        score += 1
        reasons.append(f"平均负面情绪分数达到 {negative_score_avg:.0%}")

    if sad_score_avg >= 0.2:
        score += 1
        reasons.append(f"悲伤情绪平均分数达到 {sad_score_avg:.0%}")

    if score >= 4:
        level = "high"
    elif score >= 2:
        level = "medium"
    else:
        level = "low"

    return level, "; ".join(reasons) if reasons else "视频情绪整体平稳", SUGGESTIONS[level]
