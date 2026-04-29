from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.class_model import Class
from app.models.record import RiskWarning
from app.utils.deps import get_current_user, require_role

router = APIRouter(prefix="/warnings", tags=["预警"])


@router.get("/my")
def my_warnings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    warnings = (
        db.query(RiskWarning)
        .filter(RiskWarning.user_id == user.id)
        .order_by(RiskWarning.created_at.desc())
        .limit(20)
        .all()
    )
    return {"code": 200, "message": "ok", "data": [{"id": w.id, "level": w.warning_level, "reason": w.reason, "status": w.status, "created_at": w.created_at.isoformat()} for w in warnings]}


@router.get("/admin/list")
def admin_list(
    user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    warnings = (
        db.query(RiskWarning)
        .order_by(RiskWarning.created_at.desc())
        .limit(100)
        .all()
    )

    user_ids = list(set(w.user_id for w in warnings))
    users = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()}

    # 批量查班级名
    class_ids = {u.class_id for u in users.values() if u.class_id}
    class_map = {}
    if class_ids:
        for c in db.query(Class).filter(Class.id.in_(class_ids)).all():
            class_map[c.id] = c.name

    data = []
    for w in warnings:
        u = users.get(w.user_id)
        data.append({
            "id": w.id,
            "user_id": w.user_id,
            "username": u.username if u else None,
            "real_name": u.real_name if u else None,
            "class_name": class_map.get(u.class_id) if u and u.class_id else None,
            "warning_level": w.warning_level,
            "reason": w.reason,
            "suggestion": w.suggestion,
            "status": w.status,
            "created_at": w.created_at.isoformat(),
            "handled_at": w.handled_at.isoformat() if w.handled_at else None,
        })

    return {"code": 200, "message": "ok", "data": data}


@router.put("/admin/{warning_id}/status")
def update_status(
    warning_id: int,
    user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    warning = db.get(RiskWarning, warning_id)
    if not warning:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="预警记录不存在")

    warning.status = "handled"
    warning.handled_at = datetime.now()
    db.commit()

    return {"code": 200, "message": "已标记为已处理", "data": None}
