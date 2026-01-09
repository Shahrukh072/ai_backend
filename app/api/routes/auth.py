from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token, GoogleAuthRequest
from app.services.auth_service import AuthService
from app.services.oauth_service import OAuthService
from app.core.security import verify_token
from jose import jwt
from app.config import settings

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        auth_service = AuthService(db)
        user = auth_service.create_user(user_data)
        return user
    except HTTPException:
        # Re-raise HTTPExceptions (like duplicate email)
        raise
    except Exception as e:
        # Log unexpected errors and return generic message
        logger.exception(f"Unexpected error during user registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration"
        )


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
    """Debug endpoint to check current configuration (development only)"""
    import os
    if os.getenv("ENV") != "development":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debug endpoints are only available in development"
        )
    return {
        "secret_key_length": len(settings.SECRET_KEY),
        "algorithm": settings.ALGORITHM,
        "token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES
    }


@router.post("/google", response_model=Token)
async def google_auth(
    auth_request: GoogleAuthRequest,
    db: Session = Depends(get_db)
):
    """Authenticate with Google OAuth token"""
    if not settings.GOOGLE_OAUTH_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured"
        )
    
    oauth_service = OAuthService(db)
    result = oauth_service.authenticate_google_user(auth_request.token.get_secret_value())
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"access_token": result["access_token"], "token_type": result["token_type"]}


@router.get("/debug/token")
async def debug_token(authorization: str = Header(None)):
    """Debug endpoint to check token verification (development only)"""
    import os
    import logging
    logger = logging.getLogger(__name__)
    
    if os.getenv("ENV") != "development":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debug endpoints are only available in development"
        )
    
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
        
        # Log detailed info server-side only
        logger.debug(f"Token debug - verified: {verified_payload is not None}, unverified payload keys: {list(unverified.keys())}")
        
        return {
            "verified": verified_payload is not None,
            "algorithm": settings.ALGORITHM,
            "token_length": len(token)
        }
    except Exception as e:
        logger.exception(f"Token debug error: {e}")
        return {"error": "Failed to process token", "error_type": type(e).__name__}
