from fastapi import FastAPI, HTTPException, Query, Body, Depends
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlmodel import Session, select
from starlette import status

from auth import create_access_token, get_current_customer
from models import Credential, CustomerCreate, Customer, AccountBase, Account, AllowedCountry, AccountPublic, \
    TokenResponse
from utils import generate_iban, generate_password
from contextlib import asynccontextmanager
from db import init_db, get_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()          # Startup
    yield
    print("Goodbye!")  # Shutdown

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello from OpenBankAPI"}

@app.post(
    "/register",
    description="Onboard a new customer and automatically open their first account.",
    tags=["Customer"],
    response_model=Credential,
    responses={
        201: {"description": "Customer registered and account created"},
        403: {"description": "Registration not allowed from this country"},
        409: {"description": "Username already exists"},
    }
)
async def register(
    customer_data: CustomerCreate = Body(...),
    session: Session = Depends(get_session)
) -> Credential:
    # Country check
    allowed = session.get(AllowedCountry, customer_data.country)
    if not allowed:
        raise HTTPException(status_code=403, detail="Registration not allowed from this country")

    # Username check
    existing = session.exec(select(Customer).where(Customer.username == customer_data.username)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists")

    # Create customer and account
    password = generate_password()
    customer = Customer(
        password=password,
        **customer_data.model_dump()
    )

    iban = generate_iban()
    account = Account(
        iban=iban,
        customer_id=None # will be set by relationship
    )

    # Link customer and account
    customer.accounts.append(account)

    session.add(customer) # account is being added implicitly
    session.commit()

    return Credential(username=customer_data.username, password=password)


@app.post(
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
    # Find customer with matching username
    customer = session.exec(
        select(Customer).where(Customer.username == credential.username)
    ).first()

    if not customer or customer.password != credential.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token_response = TokenResponse(
        message = "Logon successful",
        access_token=create_access_token(username=credential.username),
        token_type="bearer"
    )
    return token_response

@app.post(
    "/openaccount",
    tags=["Account"],
    response_model=AccountPublic,
    responses={
        201: {"description": "Account created successfully"},
        401: {"description": "Invalid or expired token"},
        404: {"description": "Customer not found"},
    }
)
async def open_account(
    customer: Customer = Depends(get_current_customer),
    account_type: str = Body(..., description="Type of account to be opened, for example, 'checking' or 'saving'"),
    session: Session = Depends(get_session)
) -> AccountPublic:
    account = Account(
        iban=generate_iban(),
        account_type=account_type,
        customer_id=None  # will be set by relationship
    )
    customer.accounts.append(account)
    session.add(customer)
    session.commit()
    session.refresh(account)

    return account


@app.get(
    "/overview",
    description="List all accounts owned by the customer.",
    tags=["Account"],
    response_model=list[AccountPublic],
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

    return accounts