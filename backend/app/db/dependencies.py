from app.db.postgres import AsyncSessionLocal

async def get_postgres_db():
    async with AsyncSessionLocal() as db:
        yield db
    