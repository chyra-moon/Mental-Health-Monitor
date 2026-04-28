from sqlalchemy import Column, Integer, String, Enum, DateTime, DECIMAL, JSON, Text, func
from app.database import Base


class EmotionRecord(Base):
    __tablename__ = "emotion_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    dominant_emotion = Column(String(20), nullable=False)
    confidence = Column(DECIMAL(5, 4), nullable=True)
    emotion_scores = Column(JSON, nullable=True)
    risk_level = Column(Enum("low", "medium", "high"), default="low")
    suggestion = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class QuestionnaireRecord(Base):
    __tablename__ = "questionnaire_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    total_score = Column(Integer, nullable=False, default=0)
    answers = Column(JSON, nullable=True)
    risk_level = Column(Enum("low", "medium", "high"), default="low")
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class RiskWarning(Base):
    __tablename__ = "risk_warnings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    warning_level = Column(Enum("low", "medium", "high"), nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(Enum("pending", "handled"), nullable=False, default="pending")
    suggestion = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    handled_at = Column(DateTime, nullable=True)


class InterventionSuggestion(Base):
    __tablename__ = "intervention_suggestions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    warning_id = Column(Integer, nullable=True)
    content = Column(Text, nullable=False)
    source = Column(Enum("system", "admin"), nullable=False, default="system")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
