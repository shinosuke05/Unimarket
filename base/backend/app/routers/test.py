from fastapi import APIRouter

router = APIRouter(
    prefix="/api",
    tags=["Test"]
)

@router.get("/test")
def test_connection():
    return {
        "success": True,
        "message": "Frontend connected to FastAPI successfully"
    }