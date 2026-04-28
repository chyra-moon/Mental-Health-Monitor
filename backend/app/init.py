"""项目初始化：创建数据库表和默认管理员账号。"""

from app.database import engine, SessionLocal, Base
from app.models import User
from app.utils.security import hash_password


def init():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                password_hash=hash_password("admin123"),
                real_name="系统管理员",
                role="admin",
            )
            db.add(admin)
            db.commit()
            print("默认管理员已创建（账号: admin, 密码: admin123）")
        else:
            print("管理员账号已存在，跳过")
    finally:
        db.close()


if __name__ == "__main__":
    init()
