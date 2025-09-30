from enum import Enum
from typing import List

from pydantic import BaseModel, field_validator
from datetime import date, datetime, timezone
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship

class AccountType(str, Enum):
    """Type of account allowed in the bank"""
    checking = "checking"
    saving = "saving"
    investment = "investment"

class AccountRequest(BaseModel):
    account_type: AccountType = Field(...)

# Shared account properties
class AccountBase(SQLModel):
    iban : str = Field(..., description="International Bank Account Number (IBAN)")
    account_type: AccountType = Field(AccountType.checking)
    balance: float = 0
    currency: str = Field("EUR", description="Currency code (ISO 4217)")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("balance")
    def validate_balance(cls, v):
        if v < 0:
            raise ValueError("Balance cannot be negative")
        return v

# account properties to response to the customer
class AccountPublic(AccountBase):
    pass

class AccountsResponse(BaseModel):
    message: str
    accounts: List[AccountPublic]

# account table
class Account(AccountBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    customer_id: UUID = Field(foreign_key="customer.id")
    customer: "Customer" = Relationship(back_populates="accounts")


# Shared customer properties
class CustomerBase(SQLModel):
    name: str = Field(..., description="Full legal name of the customer")
    dob: date = Field(..., description="Date of birth (YYYY-MM-DD). Must be 18 years or older to register")
    address: str = Field(..., description="Residential address")
    country: str = Field(..., min_length=2, max_length=2, description="2-letter ISO country code of residence. Must be one of the allowed countries (NL, BE, DE)")
    id_document: str = Field(..., description="Government-issued ID number, e.g., passport number")
    username: str = Field(..., min_length=3, max_length=20, description="Unique username for login (3~20 characters)")

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
    accounts: list[Account] = Relationship(back_populates="customer")
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# allowed_countries table
class AllowedCountry(SQLModel, table=True):
    iso_code: str = Field(primary_key=True, min_length=2, max_length=2,
                          description="2-letter ISO country code allowed for registration")


class Credential(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    message: str
    access_token: str
    token_type: str