from fastapi import Depends, Body, APIRouter, HTTPException
from sqlmodel import Session
from starlette import status
from auth import get_current_customer
from db import get_session
from models import Customer, Account
from schemas import AccountRequest, AccountPublic, AccountsResponse
from utils import generate_iban

router = APIRouter(prefix="/accounts", tags=["Account"])

@router.post(
    "/open",
    response_model=AccountPublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Account created successfully"},
        401: {"description": "Invalid or expired token"},
        404: {"description": "Customer not found"},
    }
)
async def open_account(
    customer: Customer = Depends(get_current_customer),
    account_request: AccountRequest = Body(...),
    session: Session = Depends(get_session)
) -> AccountPublic:
    account = Account(
        iban=generate_iban(),
        account_type=account_request.account_type,
        customer_id=None  # will be set by relationship
    )
    customer.accounts.append(account)
    session.add(customer)
    session.commit()
    session.refresh(account)

    return account


@router.get(
    "/overview",
    description="List all accounts owned by the customer.",
    tags=["Account"],
    response_model=AccountsResponse,
    response_description="A list of accounts with IBAN, type, balance, currency, and creation timestamp",
    responses={
        200: {"description": "Accounts retrieved successfully"},
        401: {"description": "Invalid or expired token"},
        404: {"description": "No accounts found for the customer"},
    }
)
async def overview(customer: Customer = Depends(get_current_customer)) -> list[AccountPublic]:
    # Find the account
    accounts = customer.accounts
    if not accounts:
        raise HTTPException(status_code=404, detail="Account not found")

    return AccountsResponse(message="Accounts retrieved successfully", accounts=accounts)