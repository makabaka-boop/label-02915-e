from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=4, max_length=100, description="密码")


class LoginResponse(BaseModel):
    token: str
    username: str
    nickname: str
    user_id: int
