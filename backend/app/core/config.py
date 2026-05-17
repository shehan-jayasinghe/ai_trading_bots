from dotenv import load_dotenv
import os

load_dotenv()

AUTH_SECRET = os.getenv("AUTH_SECRET")
JWT_ALGORITHM = "HS256"
POSTGRES_DATABASE_URL = os.getenv("POSTGRES_DATABASE_URL")

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
RELOAD = os.getenv("RELOAD", "true").lower() in ("1", "true", "yes")

KAFKA_ENABLED = os.getenv("KAFKA_ENABLED", "false").lower() in ("1", "true", "yes")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_SCHEDULED = os.getenv("KAFKA_TOPIC_SCHEDULED", "workflow.scheduled")