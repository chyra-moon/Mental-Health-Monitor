from pydantic import BaseModel, Field, field_validator


def validate_bcrypt_password(value: str) -> str:
    if len(value.encode("utf-8")) > 72:
        raise ValueError("密码不能超过 72 字节，中文或特殊字符会占用多个字节")
    return value


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=50)

    @field_validator("password")
    @classmethod
    def check_password_length(cls, value: str) -> str:
        return validate_bcrypt_password(value)


class LoginRequest(BaseModel):
    username: str
    password: str

    @field_validator("password")
    @classmethod
    def check_password_length(cls, value: str) -> str:
        return validate_bcrypt_password(value)


class ProfileUpdateRequest(BaseModel):
    real_name: str = Field(..., min_length=1, max_length=50)
    gender: str | None = None
    class_id: int | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    real_name: str | None = None
    role: str
    gender: str | None = None
    class_id: int | None = None
    class_name: str | None = None

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    token: str
    user: UserResponse
