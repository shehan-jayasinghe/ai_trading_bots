from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.db.postgres import Base


class Workflow(Base):
    __tablename__ = "Workflow"

    id = Column(String, primary_key=True)
    user_id = Column("userId", String)
    name = Column(String)
    trading_pair = Column("tradingPair", String)
    trading_type = Column("tradingType", String)
    status = Column(String)
    starting_time = Column("startingTime", DateTime(timezone=True))
    one_day_minimum_trade = Column("oneDayMinimumTrade", String)
    created_at = Column(
        "createdAt",
        DateTime(timezone=True),
        server_default=func.now(),
    )
    graph_definition = Column("graphDefinition", JSONB, nullable=True)
    deriv_app_id = Column("derivAppId", String, nullable=True)
    deriv_api_token = Column("derivApiToken", String, nullable=True)
    last_trade_result = Column("lastTradeResult", JSONB, nullable=True)