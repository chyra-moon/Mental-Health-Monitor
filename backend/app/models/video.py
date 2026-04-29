from sqlalchemy import Column, Integer, String, Enum, DateTime, DECIMAL, JSON, Text, func
from app.database import Base


class VideoAnalysisSession(Base):
    __tablename__ = "video_analysis_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, nullable=False, index=True)
    admin_id = Column(Integer, nullable=False, index=True)
    frame_interval_ms = Column(Integer, nullable=False, default=1000)
    status = Column(Enum("running", "completed", "failed"), nullable=False, default="running")
    video_path = Column(Text, nullable=True)
    video_filename = Column(String(255), nullable=True)
    video_content_type = Column(String(100), nullable=True)
    total_frames = Column(Integer, nullable=False, default=0)
    analyzed_frames = Column(Integer, nullable=False, default=0)
    dominant_emotion = Column(String(20), nullable=True)
    average_emotion_scores = Column(JSON, nullable=True)
    emotion_distribution = Column(JSON, nullable=True)
    negative_ratio = Column(DECIMAL(5, 4), nullable=True)
    dominant_confidence = Column(DECIMAL(5, 4), nullable=True)
    risk_level = Column(Enum("low", "medium", "high"), nullable=False, default="low")
    reason = Column(Text, nullable=True)
    suggestion = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=False, server_default=func.now())
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class VideoFrameEmotionRecord(Base):
    __tablename__ = "video_frame_emotion_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, nullable=False, index=True)
    student_id = Column(Integer, nullable=False, index=True)
    frame_index = Column(Integer, nullable=False)
    timestamp_ms = Column(Integer, nullable=False, default=0)
    analysis_status = Column(Enum("ok", "no_face", "error"), nullable=False, default="ok")
    dominant_emotion = Column(String(20), nullable=True)
    confidence = Column(DECIMAL(5, 4), nullable=True)
    emotion_scores = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
