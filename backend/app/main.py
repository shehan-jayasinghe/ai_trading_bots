import logging

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError
from app.middleware.auth import get_current_user
from app.routes.public.hello import router as public_hello_router
from app.routes.protected.hello import router as protected_hello_router
from app.routes.protected.workflow_routes import router as workflow_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Trading Workflow API",
    version="0.1.0",
)


@app.exception_handler(AppError)
async def app_error_handler(_request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception):
    if isinstance(exc, AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    logger.exception("Unhandled server error")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
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
app.include_router(
    workflow_router,
    dependencies=[Depends(get_current_user)],
)


if __name__ == "__main__":
    import uvicorn

    from app.core.config import HOST, PORT, RELOAD

    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
    )
