from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
import bcrypt
from app.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    """Hash a password"""
    # Encode password to bytes
    password_bytes = password.encode('utf-8')
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token"""
    if not token:
        return None
    
    # Strip any whitespace
    token = token.strip()
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM],
            options={"verify_signature": True, "verify_exp": True}
        )
        return payload
    except ExpiredSignatureError as e:
        # Token has expired
        print(f"[TOKEN VERIFY] Token expired: {e}")
        return None
    except JWTClaimsError as e:
        # Invalid token claims
        print(f"[TOKEN VERIFY] JWT claims error: {e}")
        return None
    except JWTError as e:
        # Other JWT errors (including signature verification failures)
        print(f"[TOKEN VERIFY] JWT error: {type(e).__name__}: {e}")
        return None
    except Exception as e:
        # Any other unexpected errors
        print(f"[TOKEN VERIFY] Unexpected error: {type(e).__name__}: {e}")
        return None

