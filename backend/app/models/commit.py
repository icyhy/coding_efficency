from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional

from app.core.database import Base


class Commit(Base):
    __tablename__ = "commits"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    repository_id: Mapped[int] = mapped_column(Integer, ForeignKey("repositories.id"), nullable=False, index=True)
    commit_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    author_name: Mapped[str] = mapped_column(String(255), nullable=False)
    author_email: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    commit_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self) -> dict:
        """Convert commit object to dictionary"""
        return {
            "id": self.id,
            "repository_id": self.repository_id,
            "commit_hash": self.commit_hash,
            "author_name": self.author_name,
            "author_email": self.author_email,
            "message": self.message,
            "commit_date": self.commit_date.isoformat() if self.commit_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        return f"<Commit(id={self.id}, hash='{self.commit_hash[:8]}', author='{self.author_name}')>"