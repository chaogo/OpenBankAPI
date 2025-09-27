from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator, Field
from datetime import date, datetime, timezone

app = FastAPI()

# Schemas
class Customer(BaseModel):
    name: str
    dob: date
    address: str
    country: str
    id_document: str
    username: str
    password: str | None = None
    account_id: str | None = None

    @field_validator("dob")
    def validate_dob(cls, v: date):
        age = (date.today() - v).days // 365
        if age < 18:
            raise ValueError("Customer must be at least 18 years old")
        return v

class Account(BaseModel):
    customer_id: str
    iban : str
    account_type: str = "checking"
    balance: float = 0
    currency: str = "EUR"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Credential(BaseModel):
    username: str
    password: str

# Mock database
customers = []
accounts = []
allowed_countries = ["NL", "BE", "DE"]

@app.get("/")
async def root():
    return {"message": "Hello from OpenBankAPI"}

@app.post("/register", response_model=Credential)
async def register(customer: Customer):
    # Country check
    if customer.country not in allowed_countries:
        raise HTTPException(status_code=403, detail="Registration not allowed from this country")

    # Username check
    if any(c.username == customer.username for c in customers):
        raise HTTPException(status_code=409, detail="Username already exists")

    # Create customer and account
    iban = "generate_iban()"
    account = Account(
        customer_id="to be added",
        iban=iban
    )

    accounts.append(account)

    password = "generate_password()"
    customer.account_id = "to be added"
    customer.password = password
    customers.append(customer)

    # Response with username and generated password
    credential = Credential(username=customer.username, password=password)

    return credential


@app.post("/logon")
async def logon(credential: Credential):
    # Find customer with matching username
    customer = next((c for c in customers if c.username == credential.username), None)
    if not customer or customer.password != credential.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"message": "Login successful"}
