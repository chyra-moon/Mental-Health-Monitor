from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "mysql+pymysql://root:root@localhost:3306/mental_health"
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_expire_hours: int = 24
    model_backend: str = "deepface"
    upload_dir: str = "./uploads/temp"
    video_dir: str = "./vedio"
    cors_origins: str = "http://localhost:5173"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
