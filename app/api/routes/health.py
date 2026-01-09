from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "AI Document SaaS API"}


@router.get("/health")
async def health_check():
    return {"status": "healthy"}

