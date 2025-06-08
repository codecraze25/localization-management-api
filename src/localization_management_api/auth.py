from datetime import datetime, timedelta
from typing import Optional
import jwt
import hashlib
import secrets
from .models import User, LoginRequest, RegisterRequest, LoginResponse

# Simple in-memory storage for demo purposes
# In production, this should be a proper database
USERS_DB = {}
ACTIVE_TOKENS = set()

# JWT Configuration
JWT_SECRET = "your-secret-key-change-this-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256 with salt"""
        salt = "localization-salt"  # In production, use random salt per user
        return hashlib.sha256((password + salt).encode()).hexdigest()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return AuthService.hash_password(password) == hashed

    @staticmethod
    def create_user(register_data: RegisterRequest) -> User:
        """Create a new user"""
        user_id = secrets.token_urlsafe(16)

        # Check if username already exists
        for user_data in USERS_DB.values():
            user = user_data["user"]
            if user.username == register_data.username:
                raise ValueError("Username already exists")
            if user.email == register_data.email:
                raise ValueError("Email already exists")

        user = User(
            id=user_id,
            username=register_data.username,
            email=register_data.email,
            full_name=register_data.full_name,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True
        )

        # Store user with hashed password
        USERS_DB[user_id] = {
            "user": user,
            "password_hash": AuthService.hash_password(register_data.password)
        }

        return user

    @staticmethod
    def authenticate_user(login_data: LoginRequest) -> Optional[User]:
        """Authenticate user with username/password"""
        for user_data in USERS_DB.values():
            user = user_data["user"]
            if (user.username == login_data.username and
                AuthService.verify_password(login_data.password, user_data["password_hash"]) and
                user.is_active):
                return user
        return None

    @staticmethod
    def create_access_token(user: User) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        payload = {
            "sub": user.id,
            "username": user.username,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        ACTIVE_TOKENS.add(token)
        return token

    @staticmethod
    def verify_token(token: str) -> Optional[User]:
        """Verify JWT token and return user"""
        try:
            if token not in ACTIVE_TOKENS:
                return None

            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("sub")

            if user_id and user_id in USERS_DB:
                return USERS_DB[user_id]["user"]
            return None
        except jwt.PyJWTError:
            return None

    @staticmethod
    def logout(token: str) -> bool:
        """Logout user by invalidating token"""
        if token in ACTIVE_TOKENS:
            ACTIVE_TOKENS.remove(token)
            return True
        return False

    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[User]:
        """Get user by ID"""
        if user_id in USERS_DB:
            return USERS_DB[user_id]["user"]
        return None

# Create a default admin user for testing
def initialize_default_users():
    """Initialize default users for testing"""
    if not USERS_DB:  # Only create if no users exist
        admin_user = RegisterRequest(
            username="admin",
            email="admin@example.com",
            password="admin123",
            full_name="System Administrator"
        )

        demo_user = RegisterRequest(
            username="demo",
            email="demo@example.com",
            password="demo123",
            full_name="Demo User"
        )

        try:
            AuthService.create_user(admin_user)
            AuthService.create_user(demo_user)
            print("Default users created: admin/admin123, demo/demo123")
        except ValueError as e:
            print(f"Users already exist: {e}")

# Initialize default users
initialize_default_users()