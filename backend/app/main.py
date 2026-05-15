from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middleware.auth import get_current_user
from app.routes.public.hello import router as public_hello_router
from app.routes.protected.hello import router as protected_hello_router

app = FastAPI(
    title="Trading Workflow API",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(public_hello_router)
app.include_router(
    protected_hello_router,
    dependencies=[Depends(get_current_user)],
)
