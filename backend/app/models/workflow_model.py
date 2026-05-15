from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.sql import func

from app.db.postgres import Base


class Workflow(Base):

    __tablename__ = "workflows"

    id = Column(String, primary_key=True)

    user_id = Column(String)

    name = Column(String)

    trading_pair = Column(String)

    trading_type = Column(String)

    status = Column(String)

    starting_time = Column(DateTime(timezone=True))

    one_day_minimum_trade = Column(String)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )