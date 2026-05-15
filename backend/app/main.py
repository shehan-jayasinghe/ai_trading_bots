from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middleware.auth import get_current_user
from app.routes.public.hello import router as public_hello_router
from app.routes.protected.hello import router as protected_hello_router
from app.routes.protected.workflow_routes import router as workflow_router

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

#public routes
app.include_router(public_hello_router)
#protected routes
app.include_router(protected_hello_router, dependencies=[Depends(get_current_user)])
app.include_router( workflow_router,dependencies=[Depends(get_current_user)])


if __name__ == "__main__":
    import uvicorn

    from app.core.config import HOST, PORT, RELOAD

    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
    )
