from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load .env so the configured model provider can read its API key.
load_dotenv()


class Settings(BaseSettings):
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_refresh_token: str | None = None
    database_url: str | None = None
    # classifier_model: str = "anthropic:claude-haiku-5-5"
    # agent_model: str = "anthropic:claude-sonnet-5-5"
    classifier_model: str = "groq:openai/gpt-oss-20b"
    agent_model: str = "groq:openai/gpt-oss-20b"
    poll_interval_seconds: int = 60
    dashboard_username: str = "admin"
    dashboard_password: str = ""


settings = Settings()