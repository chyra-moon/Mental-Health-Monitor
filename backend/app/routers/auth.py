from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.user import User
from app.models.class_model import Class
from app.schemas.user import RegisterRequest, LoginRequest, ProfileUpdateRequest, UserResponse
from app.utils.security import hash_password, verify_password, create_token
from app.utils.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["认证"])


def _build_user_response(user: User) -> dict:
    """构建用户响应，附带班级名。"""
    data = UserResponse.model_validate(user).model_dump()
    if user.class_id:
        data["class_name"] = _get_class_name(user.class_id, user)
    return data


def _get_class_name(class_id: int, user: User) -> str:
    # 尝试从 relationship 取，否则用原 class_name 字段做兼容
    return getattr(user, "_class_name", str(class_id))


@router.post("/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")

    user = User(
        username=body.username,
        password_hash=hash_password(body.password),
        role="student",
    )
    db.add(user)
    db.commit()

    return {"code": 200, "message": "注册成功", "data": None}


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    if user.status != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已被禁用")

    token = create_token(user.id, user.role)

    # 获取班级名
    class_name = None
    if user.class_id:
        cls = db.get(Class, user.class_id)
        class_name = cls.name if cls else None

    resp = UserResponse.model_validate(user).model_dump()
    resp["class_name"] = class_name

    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "token": token,
            "user": resp,
        },
    }


@router.get("/me")
def get_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    class_name = None
    if user.class_id:
        cls = db.get(Class, user.class_id)
        class_name = cls.name if cls else None

    resp = UserResponse.model_validate(user).model_dump()
    resp["class_name"] = class_name

    return {"code": 200, "message": "ok", "data": resp}


@router.put("/profile")
def update_profile(
    body: ProfileUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅学生可完善个人信息")

    if user.real_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="信息已完善，如需修改请联系管理员")

    if body.class_id is not None:
        cls = db.get(Class, body.class_id)
        if not cls:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="班级不存在")

    user.real_name = body.real_name
    if body.gender is not None:
        user.gender = body.gender
    if body.class_id is not None:
        user.class_id = body.class_id

    db.commit()
    db.refresh(user)

    # 自动创建学生视频文件夹 vedio/{班级名}/{学生名}/
    if user.class_id and user.real_name:
        cls = db.get(Class, user.class_id)
        if cls:
            from pathlib import Path
            from app.config import settings
            (Path(settings.video_dir) / cls.name / user.real_name).mkdir(parents=True, exist_ok=True)

    class_name = None
    if user.class_id:
        cls = db.get(Class, user.class_id)
        class_name = cls.name if cls else None

    resp = UserResponse.model_validate(user).model_dump()
    resp["class_name"] = class_name

    return {"code": 200, "message": "个人信息更新成功", "data": resp}
