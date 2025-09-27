import uuid

from fastapi import FastAPI, HTTPException, Query, Body

from schemas import Credential, CustomerBase, CustomerCreate, CustomerDB, AccountBase, AccountDB
from utils import generate_iban, generate_password

app = FastAPI()

# Mock database
customers = []
accounts = []
allowed_countries = ["NL", "BE", "DE"]

@app.get("/")
async def root():
    return {"message": "Hello from OpenBankAPI"}

@app.post("/register", response_model=Credential)
async def register(customer_data: CustomerCreate = Body(...)) -> Credential:
    # Country check
    if customer_data.country not in allowed_countries:
        raise HTTPException(status_code=403, detail="Registration not allowed from this country")

    # Username check
    if any(c.username == customer_data.username for c in customers):
        raise HTTPException(status_code=409, detail="Username already exists")

    # Create customer and account
    account_id = uuid.uuid4()
    customer_id = uuid.uuid4()

    iban = generate_iban()
    account = AccountDB(
        id=account_id,
        customer_id=customer_id,
        iban=iban
    )
    accounts.append(account)

    password = generate_password()
    customer = CustomerDB(
        id=customer_id,
        password=password,
        account_id=account_id,
        **customer_data.model_dump()
    )
    customers.append(customer)

    # Response with username and generated password
    credential = Credential(username=customer_data.username, password=password)

    return credential


@app.post("/logon")
async def logon(credential: Credential):
    # Find customer with matching username
    customer = next((c for c in customers if c.username == credential.username), None)
    if not customer or customer.password != credential.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"message": "Logon successful"}

@app.get("/overview", response_model=AccountBase)
async def overview(username: str = Query(..., description="Customer username")):
    # Find the customer
    customer = next((c for c in customers if c.username == username), None)
    if not customer:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Find the account
    account = next((a for a in accounts if a.customer_id == customer.id), None)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return account