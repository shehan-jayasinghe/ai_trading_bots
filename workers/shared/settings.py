from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    kafka_bootstrap: str = "localhost:9092"
    postgres_database_url: str = ""
    deriv_ws_endpoint: str = "wss://ws.derivws.com/websockets/v3"
    openai_api_key: str = ""
    planner_tick_seconds: int = 30

    topic_scheduled: str = "workflow.scheduled"
    topic_execute: str = "workflow.execute"
    topic_run_status: str = "workflow.run.status"


settings = Settings()
