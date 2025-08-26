from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, List

from app.core.database import Base


class Repository(Base):
    __tablename__ = "repositories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    api_key_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False, default="yunxiao")
    project_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_tracked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sync_status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # Relationships
    # commits: Mapped[List["Commit"]] = relationship("Commit", back_populates="repository", cascade="all, delete-orphan")
    # merge_requests: Mapped[List["MergeRequest"]] = relationship("MergeRequest", back_populates="repository", cascade="all, delete-orphan")
    
    def to_dict(self) -> dict:
        """Convert repository object to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "url": self.url,
            "platform": self.platform,
            "project_id": self.project_id,
            "is_active": self.is_active,
            "is_tracked": self.is_tracked,
            "last_sync_at": self.last_sync_at.isoformat() if self.last_sync_at else None,
            "sync_status": self.sync_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self) -> str:
        return f"<Repository(id={self.id}, name='{self.name}', platform='{self.platform}')>"