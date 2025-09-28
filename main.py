from fastapi import FastAPI, HTTPException, Query, Body, Depends
from sqlmodel import Session, select
from models import Credential, CustomerCreate, Customer, AccountBase, Account
from utils import generate_iban, generate_password
from contextlib import asynccontextmanager
from db import init_db, get_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()          # Startup
    yield
    print("Goodbye!")  # Shutdown

app = FastAPI(lifespan=lifespan)

# Mock database
allowed_countries = ["NL", "BE", "DE"]

@app.get("/")
async def root():
    return {"message": "Hello from OpenBankAPI"}

@app.post("/register", response_model=Credential)
async def register(
    customer_data: CustomerCreate = Body(...),
    session: Session = Depends(get_session)
) -> Credential:
    # Country check
    if customer_data.country not in allowed_countries:
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
    customer.account = account

    session.add(customer) # account is being added implicitly
    session.commit()
    session.refresh(customer)
    session.refresh(account)

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

@app.get("/overview", response_model=AccountBase)
async def overview(
    username: str = Query(..., description="Customer username"),
    session: Session = Depends(get_session)
) -> Account:
    # Find the customer
    customer = session.exec(
        select(Customer).where(Customer.username == username)
    ).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Find the account
    account = customer.account
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return account