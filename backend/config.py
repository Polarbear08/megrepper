"""
Backend configuration loaded from environment variables.
Uses pydantic-settings for validation and automatic environment variable loading.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # AWS Configuration
    aws_region: str = os.getenv('AWS_REGION', 'ap-northeast-1')
    aws_access_key_id: Optional[str] = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key: Optional[str] = os.getenv('AWS_SECRET_ACCESS_KEY')

    # Application Configuration
    app_env: str = os.getenv('APP_ENV', 'development')
    app_name: str = os.getenv('APP_NAME', 'megrepper')

    # Server Configuration
    host: str = os.getenv('HOST', '0.0.0.0')
    port: int = int(os.getenv('PORT', '8000'))
    reload: bool = os.getenv('RELOAD', 'true').lower() == 'true'

    # CORS Configuration
    allowed_origins: list[str] = [
        origin.strip()
        for origin in os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost').split(',')
    ]

    @property
    def is_development(self) -> bool:
        return self.app_env == 'development'

    @property
    def is_production(self) -> bool:
        return self.app_env == 'production'

    class Config:
        env_file = '.env.local'
        env_file_encoding = 'utf-8'
        case_sensitive = False


# Global settings instance
settings = Settings()
