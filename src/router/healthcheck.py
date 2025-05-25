from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/health_check")
async def health_check():
    return JSONResponse(
        content={"message": "success"},
        status_code=200
    )