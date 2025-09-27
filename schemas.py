from pydantic import BaseModel, field_validator, Field
from datetime import date, datetime, timezone
from uuid import UUID

# Shared customer properties
class CustomerBase(BaseModel):
    name: str
    dob: date
    address: str
    country: str
    id_document: str
    username: str

# Properties to receive via /register endpoint
class CustomerCreate(CustomerBase):
    @field_validator("dob")
    def validate_dob(cls, v: date):
        age = (date.today() - v).days // 365
        if age < 18:
            raise ValueError("Customer must be at least 18 years old")
        return v

# Properties that persist into the database
class CustomerDB(CustomerBase):
    id: UUID
    password: str
    account_id: UUID
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AccountBase(BaseModel):
    customer_id: UUID
    iban : str
    account_type: str = "checking"
    balance: float = 0
    currency: str = "EUR"

class AccountDB(AccountBase):
    id: UUID
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Credential(BaseModel):
    username: str
    password: str