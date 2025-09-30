from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4
from pydantic import field_validator
from sqlmodel import SQLModel, Field, Relationship


class AccountType(str, Enum):
    """Type of account allowed in the bank"""
    checking = "checking"
    saving = "saving"
    investment = "investment"

# Shared account properties
class AccountBase(SQLModel):
    iban : str = Field(..., description="International Bank Account Number (IBAN)")
    account_type: AccountType = Field(AccountType.checking)
    balance: Decimal = Field(default=Decimal("0.00"), description="Account balance, stored with 2 decimal places")
    currency: str = Field("EUR", description="Currency code (ISO 4217)")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("balance")
    def validate_balance(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("Balance cannot be negative")
        return v.quantize(Decimal("0.01"))

# account table
class Account(AccountBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    customer_id: UUID = Field(foreign_key="customer.id")
    customer: "Customer" = Relationship(back_populates="accounts")