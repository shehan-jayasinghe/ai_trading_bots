from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    kafka_bootstrap: str = "localhost:9092"
    postgres_database_url: str = ""
    deriv_ws_endpoint: str = "wss://ws.derivws.com/websockets/v3"
    aws_region: str = "us-west-1"
    bedrock_region: str = "us-west-1"
    bedrock_decision_model_id: str = "amazon.nova-micro-v1:0"
    sagemaker_embedding_endpoint: str = ""
    sagemaker_embedding_model_id: str = "sentence-transformers/all-MiniLM-L6-v2"
    s3_vectors_bucket_name: str = ""
    s3_vectors_index_name: str = "trade-embeddings"
    s3_vectors_embedding_dimension: int = 384
    rag_exact_window_n: int = 10
    rag_semantic_top_k: int = 5
    planner_tick_seconds: int = 30

    topic_scheduled: str = "workflow.scheduled"
    topic_execute: str = "workflow.execute"
    topic_run_status: str = "workflow.run.status"


settings = Settings()
