from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
def signup(payload: schemas.SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    if payload.role == models.UserRole.doctor and not payload.specialty:
        raise HTTPException(status_code=400, detail="Doctors must provide a specialty")

    user = models.User(
        name=payload.name,
        email=payload.email,
        password_hash=auth.hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.flush()  # get user.id before commit

    if payload.role == models.UserRole.doctor:
        doctor = models.Doctor(
            user_id=user.id,
            specialty=payload.specialty,
            bio=payload.bio or "",
            years_experience=payload.years_experience or 0,
        )
        db.add(doctor)

    db.commit()
    db.refresh(user)

    token = auth.create_access_token({"sub": str(user.id), "role": user.role.value})
    return schemas.Token(access_token=token)


@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not auth.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = auth.create_access_token({"sub": str(user.id), "role": user.role.value})
    return schemas.Token(access_token=token)


@router.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user
