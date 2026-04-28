"""一次性脚本：清洗数据库里已有的 numpy 类型数据，并验证修复。"""
import json
import numpy as np

from app.database import SessionLocal, engine
from app.models import EmotionRecord

db = SessionLocal()

# 1. 找出所有 emotion_records，修复 emotion_scores 里的 numpy 类型
records = db.query(EmotionRecord).all()
for r in records:
    if r.emotion_scores:
        fixed = {}
        for k, v in r.emotion_scores.items():
            if isinstance(v, (np.floating, np.integer)):
                fixed[k] = float(v) if isinstance(v, np.floating) else int(v)
            else:
                fixed[k] = v
        r.emotion_scores = fixed

# 2. 修复 confidence 中的 numpy 类型
for r in records:
    if isinstance(r.confidence, (np.floating, np.integer)):
        r.confidence = float(r.confidence) if isinstance(r.confidence, np.floating) else int(r.confidence)
        print(f"  已清洗：置信度从 numpy 转换为 Python 类型")

db.commit()

# 3. 验证修复结果
records = db.query(EmotionRecord).all()
for r in records:
    print(f"\n记录 #{r.id}: {r.dominant_emotion}, 置信度 {r.confidence} (类型: {type(r.confidence).__name__})")
    if r.emotion_scores:
        for k, v in r.emotion_scores.items():
            print(f"  {k}: {v} (类型: {type(v).__name__})")

db.close()
print("\n完成！")
