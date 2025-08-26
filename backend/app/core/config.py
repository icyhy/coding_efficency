from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings
import os
from pathlib import Path


class Settings(BaseSettings):
    model_config = {
        "extra": "allow",
        "case_sensitive": True,
        "env_file": ".env"
    }
    
    PROJECT_NAME: str = "Repository Analytics API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "FastAPI backend for repository analytics and management"
    API_V1_STR: str = "/api/v1"
    
    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./app.db"
    )
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8001",
        "http://localhost:8001"
    ]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Yunxiao API Settings
    YUNXIAO_BASE_URL: str = os.getenv("YUNXIAO_BASE_URL", "")
    YUNXIAO_ACCESS_TOKEN: str = os.getenv("YUNXIAO_ACCESS_TOKEN", "")
    YUNXIAO_ORG_ID: str = os.getenv("YUNXIAO_ORG_ID", "")
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100


settings = Settings()