from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.core.config import get_settings
from app.models import db_models
from app.models.schemas import UserRegisterRequest, UserLoginRequest, TokenResponse, UserPublicResponse

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email = decode_access_token(token)
    if not email:
        raise credentials_exc
    user = db.query(db_models.User).filter(db_models.User.email == email).first()
    if not user:
        raise credentials_exc
    return user

@router.post("/register", response_model=TokenResponse, status_code=201)
def register(body: UserRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(db_models.User).filter(db_models.User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = db_models.User(name=body.name, email=body.email, hashed_password=hash_password(body.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    settings = get_settings()
    token = create_access_token(subject=new_user.email)
    return TokenResponse(access_token=token, token_type="bearer", expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)

@router.post("/login", response_model=TokenResponse)
def login(body: UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(db_models.User).filter(db_models.User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    settings = get_settings()
    token = create_access_token(subject=user.email)
    return TokenResponse(access_token=token, token_type="bearer", expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)

@router.get("/me", response_model=UserPublicResponse)
def get_me(current_user: db_models.User = Depends(get_current_user)):
    return UserPublicResponse(id=current_user.id, name=current_user.name, email=current_user.email, created_at=current_user.created_at)
