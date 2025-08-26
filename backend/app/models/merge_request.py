from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional

from app.core.database import Base


class MergeRequest(Base):
    __tablename__ = "merge_requests"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    repository_id: Mapped[int] = mapped_column(Integer, ForeignKey("repositories.id"), nullable=False, index=True)
    mr_id: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    author_name: Mapped[str] = mapped_column(String(255), nullable=False)
    author_email: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    merged_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self) -> dict:
        """Convert merge request object to dictionary"""
        return {
            "id": self.id,
            "repository_id": self.repository_id,
            "mr_id": self.mr_id,
            "title": self.title,
            "description": self.description,
            "author_name": self.author_name,
            "author_email": self.author_email,
            "status": self.status,
            "created_date": self.created_date.isoformat() if self.created_date else None,
            "updated_date": self.updated_date.isoformat() if self.updated_date else None,
            "merged_date": self.merged_date.isoformat() if self.merged_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        return f"<MergeRequest(id={self.id}, mr_id='{self.mr_id}', title='{self.title[:50]}')>"