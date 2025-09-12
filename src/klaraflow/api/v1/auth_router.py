from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from klaraflow.crud import user_crud, onboarding_crud
from klaraflow.schemas import user_schema, onboarding_schema
from klaraflow.config.database import get_db
from klaraflow.core.security import create_access_token, verify_password
from klaraflow.core.exceptions import APIException
from klaraflow.core.responses import create_response

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
        raise APIException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Incorrect email or password",
            errors=["Authentication failed"]
        )
    access_token = create_access_token(data={"sub": user.email})
    token_data = user_schema.Token(access_token=access_token, token_type="bearer")
    
    return create_response(
        data=token_data.model_dump(), 
        message="Login successful",
        status_code=status.HTTP_200_OK
    )
    
@router.post("/activate", response_model=user_schema.Token)
async def activate_account(
    activation_data: onboarding_schema.OnboardingActivationRequest,
    db: AsyncSession = Depends(get_db)
):
    token_data = await onboarding_crud.activate_employee_account(db, activation_data=activation_data)
    
    return create_response(
        data=token_data, 
        message="Account activated successfully",
        status_code=status.HTTP_200_OK
    )