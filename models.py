from pydantic import BaseModel, field_validator
from datetime import date, datetime, timezone
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship

# Shared account properties
class AccountBase(SQLModel):
    iban : str
    account_type: str = "checking"
    balance: float = 0
    currency: str = "EUR"

# account table
class Account(AccountBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    customer_id: UUID = Field(foreign_key="customer.id", unique=True)
    customer: "Customer" = Relationship(back_populates="account")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


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
    @field_validator("dob")
    def validate_dob(cls, v: date):
        age = (date.today() - v).days // 365
        if age < 18:
            raise ValueError("Customer must be at least 18 years old")
        return v

# customer table
class Customer(CustomerBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    password: str
    account: Account = Relationship(back_populates="customer")
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# allowed_countries table
class AllowedCountry(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    iso_code: str = Field(index=True, unique=True, min_length=2, max_length=2)


class Credential(BaseModel):
    username: str
    password: str