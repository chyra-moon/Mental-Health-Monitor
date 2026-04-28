from sqlalchemy.orm import Session
from app.models.user import User
from app.models.record import EmotionRecord

NEGATIVE_EMOTIONS = {"sad", "angry", "fear", "disgust"}

SUGGESTIONS = {
    "low": "当前状态良好，建议保持规律作息，适当运动，继续观察。",
    "medium": "建议主动放松压力，与朋友或老师沟通，必要时寻求心理帮助。",
    "high": "建议管理员重点关注，并建议学生及时寻求专业心理老师帮助。",
}


def evaluate_risk(user_id: int, dominant_emotion: str, questionnaire_score: int | None, db: Session) -> tuple:
    """基于规则评估风险等级，返回 (risk_level, reason, suggestion)"""
    score = 0
    reasons = []

    # 1. 本次情绪是否为负面
    if dominant_emotion in NEGATIVE_EMOTIONS:
        score += 1
        reasons.append(f"本次识别情绪为负面情绪（{dominant_emotion}）")

    # 2. 最近 7 天负面情绪次数
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
        reasons.append(f"最近7天出现多次负面情绪（{week_negatives}次）")
    elif week_negatives >= 1:
        score += 1
        reasons.append(f"最近7天出现负面情绪（{week_negatives}次）")

    # 3. 问卷分数
    if questionnaire_score and questionnaire_score >= 16:
        score += 2
        reasons.append(f"心理问卷分数偏高（{questionnaire_score}分）")
    elif questionnaire_score and questionnaire_score >= 10:
        score += 1
        reasons.append(f"心理问卷分数偏高（{questionnaire_score}分）")

    # 4. 确定风险等级
    if score >= 4:
        level = "high"
    elif score >= 2:
        level = "medium"
    else:
        level = "low"

    return level, "; ".join(reasons) if reasons else "常规监测", SUGGESTIONS[level]
