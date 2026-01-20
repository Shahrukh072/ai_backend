from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import create_access_token
from google.oauth2 import id_token
from google.auth.transport import requests
from app.config import settings
from typing import Optional, Dict


class OAuthService:
    def __init__(self, db: Session):
        self.db = db
        self.google_client_id = settings.GOOGLE_OAUTH_CLIENT_ID
        if not self.google_client_id:
            import logging
            logger = logging.getLogger(__name__)
            logger.error("GOOGLE_OAUTH_CLIENT_ID is not configured in settings")

    def verify_google_token(self, token: str) -> Optional[Dict]:
        """Verify Google ID token and return user info"""
        if not self.google_client_id:
            print("ERROR: google_client_id is None in OAuthService")
            return None
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                self.google_client_id
            )

            # Verify the issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            return {
                'google_id': idinfo['sub'],
                'email': idinfo['email'],
                'full_name': idinfo.get('name', ''),
                'picture': idinfo.get('picture', ''),
            }
        except ValueError as e:
            print(f"Token verification failed: {e}")
            return None

    def get_or_create_google_user(self, google_user_info: Dict) -> User:
        """Get existing user or create new user from Google OAuth"""
        # Check if user exists by Google ID
        user = self.db.query(User).filter(
            User.google_id == google_user_info['google_id']
        ).first()

        if user:
            return user

        # Check if user exists by email (in case they signed up with email first)
        user = self.db.query(User).filter(
            User.email == google_user_info['email']
        ).first()

        if user:
            # Reject automatic account linking - require explicit user consent
            # Return None to trigger account linking flow
            return None

        # Create new user
        user = User(
            email=google_user_info['email'],
            full_name=google_user_info.get('full_name', ''),
            provider='google',
            google_id=google_user_info['google_id'],
            hashed_password=None,  # No password for OAuth users
            is_active=True
        )
        self.db.add(user)
        try:
            self.db.commit()
            self.db.refresh(user)
        except Exception as e:
            self.db.rollback()
            raise
        return user

    def authenticate_google_user(self, token: str) -> Optional[dict]:
        """Authenticate user with Google token and return JWT"""
        google_user_info = self.verify_google_token(token)
        if not google_user_info:
            return None

        user = self.get_or_create_google_user(google_user_info)
        if user is None:
            # Account linking required
            return None
        if not user.is_active:
            return None

        # Create JWT token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        # Sanitize user data before returning
        user_data = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "provider": user.provider
        }
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_data
        }

