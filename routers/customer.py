from fastapi import APIRouter, Body, HTTPException, Depends
from sqlmodel import select, Session
from db import get_session
from models import Customer, AllowedCountry, Account
from schemas import Credential, CustomerCreate
from utils import generate_password, generate_iban

router = APIRouter(prefix="/customers", tags=["Customer"])

@router.post(
    "/register",
    description="Onboard a new customer and automatically open their first account.",
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