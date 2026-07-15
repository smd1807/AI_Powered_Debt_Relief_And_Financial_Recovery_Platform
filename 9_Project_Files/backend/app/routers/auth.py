import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter()
logger = logging.getLogger("finrelief.auth")


@router.post("/register", response_model=schemas.UserOut)
def register(payload: schemas.RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        logger.warning("Registration rejected: email already exists (%s)", payload.email)
        raise HTTPException(status_code=400, detail="A user with this email already exists")

    user = models.User(
        name=payload.name,
        email=payload.email,
        password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("New user registered: %s", payload.email)
    return user


@router.post("/login", response_model=schemas.TokenOut)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password):
        logger.warning("Login failed for email=%s", payload.email)
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = create_access_token(user.user_id)
    logger.info("Login success for email=%s", payload.email)
    return schemas.TokenOut(access_token=token)


@router.get("/debug-user", response_model=schemas.UserOut)
def debug_user(current_user: models.User = Depends(get_current_user)):
    """Returns the user resolved from the current JWT — useful for verifying auth wiring."""
    return current_user
