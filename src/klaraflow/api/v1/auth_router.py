from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from klaraflow.crud import user_crud, onboarding_crud
from klaraflow.schemas import user_schema, onboarding_schema
from klaraflow.config.database import get_db
from klaraflow.core.security import create_access_token, verify_password
from klaraflow.base.exceptions import APIException
from klaraflow.base.responses import create_response

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
  
@router.post("/login")
async def login(login_data: user_schema.UserLogin, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_user_by_email(db=db, email=login_data.email)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise APIException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Incorrect email or password",
            errors=["Authentication failed"]
        )
    access_token = create_access_token(data={"sub": user.email})
    
    # Create response matching frontend expectations
    response_data = {
        "token": access_token,
        "expiresIn": 3600  # 1 hour in seconds
    }
    
    return create_response(
        data=response_data, 
        message="Login successful",
        status_code=status.HTTP_200_OK
    )
    
@router.post("/activate", response_model=user_schema.Token)
async def activate_account(
    activation_data: onboarding_schema.OnboardingActivationRequest = Body(...),
    db: AsyncSession = Depends(get_db)
):
    token_data = await onboarding_crud.activate_employee_account(db, activation_data=activation_data)
    
    return create_response(
        data=token_data, 
        message="Account activated successfully",
        status_code=status.HTTP_200_OK
    )