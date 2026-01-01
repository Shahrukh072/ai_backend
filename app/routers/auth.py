from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.services.auth_service import AuthService
from app.utils.security import verify_token
from jose import jwt
from app.config import settings

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    auth_service = AuthService(db)
    user = auth_service.create_user(user_data)
    return user


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token"""
    auth_service = AuthService(db)
    token = auth_service.authenticate_user(credentials.email, credentials.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.get("/debug/config")
async def debug_config():
    """Debug endpoint to check current configuration"""
    return {
        "secret_key_length": len(settings.SECRET_KEY),
        "secret_key_preview": settings.SECRET_KEY[:20] + "..." if len(settings.SECRET_KEY) > 20 else settings.SECRET_KEY,
        "algorithm": settings.ALGORITHM,
        "token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES
    }


@router.get("/debug/token")
async def debug_token(authorization: str = Header(None)):
    """Debug endpoint to check token verification"""
    if not authorization:
        return {"error": "No Authorization header provided"}
    
    if not authorization.startswith("Bearer "):
        return {"error": "Authorization header must start with 'Bearer '"}
    
    token = authorization.replace("Bearer ", "").strip()
    
    # Try to decode without verification first
    try:
        unverified = jwt.decode(token, options={"verify_signature": False})
        
        # Try to verify with current SECRET_KEY
        verified_payload = verify_token(token)
        
        # Try to manually decode with current SECRET_KEY to see the error
        manual_verify_error = None
        try:
            jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except Exception as e:
            manual_verify_error = str(e)
        
        # Create a test token with current settings
        from app.utils.security import create_access_token
        test_token = create_access_token(data={"sub": "1", "test": True})
        test_verified = verify_token(test_token) is not None
        
        return {
            "unverified_payload": unverified,
            "verified": verified_payload is not None,
            "verified_payload": verified_payload,
            "secret_key_length": len(settings.SECRET_KEY),
            "secret_key_preview": settings.SECRET_KEY[:10] + "..." if len(settings.SECRET_KEY) > 10 else settings.SECRET_KEY,
            "algorithm": settings.ALGORITHM,
            "manual_verify_error": manual_verify_error,
            "test_token_created": test_token[:50] + "...",
            "test_token_verified": test_verified
        }
    except Exception as e:
        return {"error": f"Failed to decode token: {str(e)}", "exception_type": type(e).__name__}
