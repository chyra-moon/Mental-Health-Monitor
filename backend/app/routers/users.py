from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.class_model import Class
from app.utils.deps import require_role

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("/admin/list")
def user_list(
    user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    students = (
        db.query(User)
        .filter(User.role == "student")
        .order_by(User.created_at.desc())
        .all()
    )

    # 批量获取班级名
    class_ids = {u.class_id for u in students if u.class_id}
    class_map = {}
    if class_ids:
        classes = db.query(Class).filter(Class.id.in_(class_ids)).all()
        class_map = {c.id: c.name for c in classes}

    return {
        "code": 200,
        "message": "ok",
        "data": [
            {
                "id": u.id,
                "username": u.username,
                "real_name": u.real_name,
                "role": u.role,
                "gender": u.gender,
                "class_id": u.class_id,
                "class_name": class_map.get(u.class_id) if u.class_id else None,
                "status": u.status,
                "created_at": u.created_at.isoformat(),
            }
            for u in students
        ],
    }
