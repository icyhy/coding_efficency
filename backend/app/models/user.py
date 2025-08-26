from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional

from app.core.database import Base
from app.core.security import verify_password, get_password_hash


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    def set_password(self, password: str) -> None:
        """Set user password (hashed)"""
        self.hashed_password = get_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check if provided password matches user's password"""
        return verify_password(password, self.hashed_password)
    
    def to_dict(self) -> dict:
        """Convert user object to dictionary"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"