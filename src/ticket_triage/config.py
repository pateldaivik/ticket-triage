from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    openai_api_key: str
    model: str = "gpt-5.4-nano"
    max_budget_usd: float = 1.0
    request_timeout_s: float = 30.0
    # USD per 1M tokens. Check against OpenAI's pricing page for your model.
    price_input_per_1m: float = 0.20
    price_output_per_1m: float = 1.25
