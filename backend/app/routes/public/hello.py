from fastapi import APIRouter

router = APIRouter(tags=["public"])


@router.get("/hello")
def public_hello():
    return {"message": "hello world"}
