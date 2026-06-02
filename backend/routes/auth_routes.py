from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, auth

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=schemas.TokenResponse)
def signup(body: schemas.SignupRequest, db: Session = Depends(get_db)):

    existing = db.query(models.User).filter(models.User.email == body.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered. Please login."
        )

    if body.gender not in ("M", "F"):
        raise HTTPException(status_code=400, detail="Gender must be M or F")

    user = models.User(
        name          = body.name,
        email         = body.email,
        password_hash = auth.hash_password(body.password),
        age           = body.age,
        gender        = body.gender
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = auth.create_token(user.id, user.email)

    return {
        "access_token": token,
        "token_type":   "bearer",
        "user": {
            "id":     user.id,
            "name":   user.name,
            "email":  user.email,
            "age":    user.age,
            "gender": user.gender
        }
    }


@router.post("/login", response_model=schemas.TokenResponse)
def login(body: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == body.email).first()

    if not user or not auth.verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    token = auth.create_token(user.id, user.email)

    return {
        "access_token": token,
        "token_type":   "bearer",
        "user": {
            "id":     user.id,
            "name":   user.name,
            "email":  user.email,
            "age":    user.age,
            "gender": user.gender
        }
    }


@router.get("/me")
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    """Returns logged-in user's profile."""
    return {
        "id":         current_user.id,
        "name":       current_user.name,
        "email":      current_user.email,
        "age":        current_user.age,
        "gender":     current_user.gender,
        "created_at": str(current_user.created_at)
    }