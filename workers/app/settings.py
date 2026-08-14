from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _split_csv(value: str) -> list[str]:
    return [p.strip() for p in value.split(",") if p.strip()]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic_candles_btc: str = "candles-btc"
    kafka_topic_candles_gold: str = "candles-gold"
    kafka_topic_market_trades: str = "market-trades"
    kafka_topic_market_orderbook: str = "market-orderbook"
    kafka_topic_market_flow: str = "market-flow"

    worker_enable_binance: bool = True
    worker_enable_binance_flow: bool = True
    worker_enable_deriv: bool = False

    binance_api_key: str = ""
    binance_api_secret: str = ""
    binance_base_url: str = "https://api.binance.com"
    binance_ws_url: str = "wss://stream.binance.com:9443/ws"
    binance_combined_ws_url: str = "wss://stream.binance.com:9443/stream"
    binance_symbol: str = "BTCUSDT"
    binance_timeframes: str = "1s,1m"
    binance_flow_liquidity_pct: float = 0.005

    deriv_app_id: str = "1089"
    deriv_token: str = ""
    deriv_ws_endpoint: str = "wss://ws.derivws.com/websockets/v3"
    deriv_symbol: str = "frxXAUUSD"
    deriv_timeframes: str = "1s,1m,2m,3m"

    host: str = "0.0.0.0"
    port: int = Field(default=8081)

    @property
    def binance_tf_list(self) -> list[str]:
        return _split_csv(self.binance_timeframes)

    @property
    def deriv_tf_list(self) -> list[str]:
        return _split_csv(self.deriv_timeframes)


@lru_cache
def get_settings() -> Settings:
    return Settings()
