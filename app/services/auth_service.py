from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, create_access_token


class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            provider="email"
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def authenticate_user(self, email: str, password: str) -> dict | None:
        """Authenticate user and return token"""
        from app.core.security import verify_password
        
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            return None
        
        # Check if user is active
        if not user.is_active:
            return None
        
        # OAuth users (Google) don't have passwords - they must use OAuth login
        if user.provider == "google" or not user.hashed_password:
            return None
        
        # Verify password for email-based users
        if not verify_password(password, user.hashed_password):
            return None
        
        # Convert user.id to string for JWT sub claim
        access_token = create_access_token(data={"sub": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer"}

