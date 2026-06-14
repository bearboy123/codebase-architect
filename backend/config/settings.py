"""
Settings and configuration for the backend.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Backend application settings."""

    # Azure OpenAI Configuration
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_model_deployment: str = "gpt-4"
    azure_openai_api_version: str = "2025-01-01-preview"

    # Server Configuration
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    debug: bool = False

    # Frontend
    frontend_url: str = "http://localhost:3000"

    # Analysis Settings
    max_analysis_time_seconds: int = 300
    max_file_size_mb: int = 50
    analyze_hidden_files: bool = False


    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        case_sensitive=False, 
        extra="ignore"
    )


# Create global settings instance
settings = Settings()
