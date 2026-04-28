from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import RegisterRequest, LoginRequest, UserResponse
from app.utils.security import hash_password, verify_password, create_token
from app.utils.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")

    user = User(
        username=body.username,
        password_hash=hash_password(body.password),
        real_name=body.real_name,
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
    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "token": token,
            "user": UserResponse.model_validate(user).model_dump(),
        },
    }


@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    return {"code": 200, "message": "ok", "data": UserResponse.model_validate(user).model_dump()}
