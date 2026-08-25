"""User business logic."""
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password, verify_password


class UserAlreadyExistsError(Exception):
    """Raised when registering with an email or username already in use."""

    def __init__(self, field: str):
        self.field = field
        super().__init__(f"User with this {field} already exists")


class InvalidCredentialsError(Exception):
    """Raised when login credentials are incorrect."""


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email.lower()).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: UUID) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_data: UserCreate) -> User:
    """Register a new user with a hashed password.

    Raises:
        UserAlreadyExistsError: Email or username is taken
    """
    if get_user_by_email(db, user_data.email):
        raise UserAlreadyExistsError("email")
    if get_user_by_username(db, user_data.username):
        raise UserAlreadyExistsError("username")

    user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=hash_password(user_data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Verify login credentials.

    Raises:
        InvalidCredentialsError: Unknown email or wrong password
    """
    user = get_user_by_email(db, email)
    if not user or not user.password_hash:
        raise InvalidCredentialsError()
    if not verify_password(password, user.password_hash):
        raise InvalidCredentialsError()
    if not user.is_active:
        raise InvalidCredentialsError()
    return user
