from fastapi import FastAPI, HTTPException, Query, Body, Depends
from sqlmodel import Session, select
from models import Credential, CustomerCreate, Customer, AccountBase, Account, AllowedCountry, AccountPublic
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

@app.post("/register", response_model=Credential)
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


@app.post("/logon")
async def logon(
    credential: Credential,
    session: Session = Depends(get_session)
):
    # Find customer with matching username
    customer = session.exec(
        select(Customer).where(Customer.username == credential.username)
    ).first()

    if not customer or customer.password != credential.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {"message": "Logon successful"}

@app.post("/openaccount", response_model=AccountPublic)
async def open_account(
    username: str = Body(...),
    password: str = Body(...),
    account_type: str = Body(...),
    session: Session = Depends(get_session)
) -> AccountPublic:
    customer = session.exec(
        select(Customer).where(Customer.username == username)
    ).first()
    if not customer or customer.password != password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

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


@app.get("/overview", response_model=list[AccountPublic])
async def overview(
    username: str = Query(..., description="Customer username"),
    session: Session = Depends(get_session)
) -> list[AccountPublic]:
    # Find the customer
    customer = session.exec(
        select(Customer).where(Customer.username == username)
    ).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Find the account
    accounts = customer.accounts
    if not accounts:
        raise HTTPException(status_code=404, detail="Account not found")

    return accounts