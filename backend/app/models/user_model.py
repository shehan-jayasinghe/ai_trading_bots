from sqlalchemy import Column, String

from app.db.postgres import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String)
    name = Column(String)