from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from klaraflow.crud import user_crud
from klaraflow.schemas import user_schema
from klaraflow.config.database import get_db
from klaraflow.core.security import create_access_token, verify_password

router = APIRouter()

@router.post("/signup", response_model=user_schema.UserPublic, status_code=status.HTTP_201_CREATED)
async def signup(user: user_schema.UserCreate, db: AsyncSession = Depends(get_db)):
  db_user = await user_crud.get_user_by_email(db, email=user.email)
  if db_user: 
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Email already registered",
    )
  return await user_crud.create_user(db=db, user=user)
  
@router.post("/login", response_model=user_schema.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
  user = await user_crud.get_user_by_email(db=db, email=form_data.username)
  if not user or not verify_password(form_data.password, user.hashed_password):
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Incorrect email or password",
      headers={"WWW-Authenticate": "Bearer"}
    )
  access_token = create_access_token(data={"sub": user.email})
  return {"access_token": access_token, "token_type": "bearer"}