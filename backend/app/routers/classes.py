from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.class_model import Class
from app.utils.deps import require_role, get_current_user

router = APIRouter(prefix="/classes", tags=["班级管理"])


class CreateClassRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)


# ---- 管理员接口 ----
admin_router = APIRouter(prefix="/admin/classes", tags=["班级管理"])


@admin_router.get("")
def list_classes(user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    classes = db.query(Class).order_by(Class.created_at).all()
    items = []
    for c in classes:
        student_count = db.query(User).filter(User.class_id == c.id, User.role == "student").count()
        items.append({
            "id": c.id,
            "name": c.name,
            "student_count": student_count,
            "created_at": c.created_at.isoformat(),
        })
    return {"code": 200, "message": "ok", "data": items}


@admin_router.post("")
def create_class(body: CreateClassRequest, user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    if db.query(Class).filter(Class.name == body.name).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="班级名已存在")

    cls = Class(name=body.name)
    db.add(cls)
    db.commit()
    db.refresh(cls)

    # 自动创建班级文件夹
    from app.config import settings
    from pathlib import Path
    (Path(settings.video_dir) / body.name).mkdir(parents=True, exist_ok=True)

    return {
        "code": 200,
        "message": "班级创建成功",
        "data": {"id": cls.id, "name": cls.name},
    }


@admin_router.delete("/{class_id}")
def delete_class(class_id: int, user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    cls = db.query(Class).filter(Class.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="班级不存在")

    student_count = db.query(User).filter(User.class_id == class_id, User.role == "student").count()
    if student_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"班级「{cls.name}」中还有 {student_count} 名学生，无法删除",
        )

    db.delete(cls)
    db.commit()
    return {"code": 200, "message": f"班级「{cls.name}」已删除", "data": None}


# ---- 学生接口（获取可选班级列表） ----
@router.get("")
def list_classes_student(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    classes = db.query(Class).order_by(Class.created_at).all()
    items = [{"id": c.id, "name": c.name} for c in classes]
    return {"code": 200, "message": "ok", "data": items}
