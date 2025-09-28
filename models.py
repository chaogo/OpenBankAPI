from pydantic import BaseModel, field_validator, Field
from datetime import date, datetime, timezone
from uuid import UUID
from sqlmodel import SQLModel, Field, Relationship

# Shared account properties
class AccountBase(SQLModel):
    iban : str
    account_type: str = "checking"
    balance: float = 0
    currency: str = "EUR"

# Properties that persist in the table account
class Account(AccountBase, table=True):
    id: UUID = Field(default=None, primary_key=True)
    customer_id: UUID = Field(foreign_key="customer.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    customer: "Customer" = Relationship(back_populates="account")

# Shared customer properties
class CustomerBase(SQLModel):
    name: str
    dob: date
    address: str
    country: str
    id_document: str
    username: str

# Properties to receive via /register endpoint
class CustomerCreate(CustomerBase):
    @field_validator("dob") # pylint: disable=no-self-argument
    def validate_dob(cls, v: date):
        age = (date.today() - v).days // 365
        if age < 18:
            raise ValueError("Customer must be at least 18 years old")
        return v

# Properties that persist in the table customer
class Customer(CustomerBase, table=True):
    id: UUID = Field(default=None, primary_key=True)
    password: str
    account_id: UUID
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    account: Account = Relationship(back_populates="customer")

class Credential(BaseModel):
    username: str
    password: str