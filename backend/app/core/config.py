from dotenv import load_dotenv
import os

load_dotenv()

AUTH_SECRET = os.getenv("AUTH_SECRET")
JWT_ALGORITHM = "HS256"
POSTGRES_DATABASE_URL = os.getenv("POSTGRES_DATABASE_URL")

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
RELOAD = os.getenv("RELOAD", "true").lower() in ("1", "true", "yes")