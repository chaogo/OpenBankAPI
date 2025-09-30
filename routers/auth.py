from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from auth import create_access_token
from db import get_session
from models import Customer
from schemas import TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])
@router.post(
    "/logon",
    tags=["Authentication"],
    response_model=TokenResponse,
    responses={
        200: {"description": "Successful login returning a JWT token"},
        401: {"description": "Invalid username or password"},
    }
)
async def logon(
    credential: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
) -> TokenResponse:
    print("hello")
    # Find customer with matching username
    customer = session.exec(
        select(Customer).where(Customer.username == credential.username)
    ).first()
    print("hello")
    if not customer or customer.password != credential.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token_response = TokenResponse(
        message = "Logon successful",
        access_token=create_access_token(username=credential.username),
        token_type="bearer"
    )
    return token_response