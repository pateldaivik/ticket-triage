from pydantic import BaseSetttings, SettingsConfigDict


class Settings(BaseSetttings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    openai_api_key: str
    model: str = "gpt-5.4-nano"
    max_budget_usd: float = 1.0
