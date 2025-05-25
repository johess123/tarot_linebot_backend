from fastapi import APIRouter, Response

router = APIRouter()

@router.head("/health_check")
async def health_check_head():
    return Response(status_code=200)