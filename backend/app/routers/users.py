from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
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
    return {
        "code": 200,
        "message": "ok",
        "data": [
            {
                "id": u.id,
                "username": u.username,
                "real_name": u.real_name,
                "gender": u.gender,
                "class_name": u.class_name,
                "status": u.status,
                "created_at": u.created_at.isoformat(),
            }
            for u in students
        ],
    }
