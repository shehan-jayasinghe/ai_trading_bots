from dotenv import load_dotenv
import os

load_dotenv()

AUTH_SECRET = os.getenv("AUTH_SECRET")
JWT_ALGORITHM = "HS256"
POSTGRES_DATABASE_URL = os.getenv("POSTGRES_DATABASE_URL")
PORT = os.getenv("PORT")