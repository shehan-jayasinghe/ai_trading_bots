from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    run_id: str = "manual-local-run"
    deriv_symbol: str = "R_10"
    trades_per_run: int = 5

    bot_data_fn: str
    bot_strategy_fn: str
    bot_decision_fn: str
    bot_execution_fn: str

    bot_settle_fn: str | None = None
    bot_guardrail_fn: str | None = None


settings = Settings()

