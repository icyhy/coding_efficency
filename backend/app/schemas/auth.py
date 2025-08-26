from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """用户基础模式"""
    username: str = Field(..., min_length=3, max_length=20, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")


class UserRegister(UserBase):
    """用户注册模式"""
    password: str = Field(..., min_length=8, description="密码")


class UserLogin(BaseModel):
    """用户登录模式"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class UserResponse(UserBase):
    """用户响应模式"""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """令牌响应模式"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模式"""
    refresh_token: str


class TokenPayload(BaseModel):
    """令牌载荷模式"""
    sub: Optional[str] = None
    exp: Optional[int] = None