from sqlalchemy import Column, Integer, String, DateTime, Text, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional, Dict, Any

from app.core.database import Base


class AnalyticsCache(Base):
    __tablename__ = "analytics_cache"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cache_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    cache_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def to_dict(self) -> dict:
        """Convert analytics cache object to dictionary"""
        return {
            "id": self.id,
            "cache_key": self.cache_key,
            "cache_data": self.cache_data,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def is_expired(self) -> bool:
        """Check if cache is expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self) -> str:
        return f"<AnalyticsCache(id={self.id}, cache_key='{self.cache_key}')>"