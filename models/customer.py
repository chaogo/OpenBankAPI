from datetime import date, datetime, timezone
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship

# Shared customer properties
class CustomerBase(SQLModel):
    name: str = Field(..., description="Full legal name of the customer")
    dob: date = Field(..., description="Date of birth (YYYY-MM-DD). Must be 18 years or older to register")
    address: str = Field(..., description="Residential address")
    country: str = Field(..., min_length=2, max_length=2, description="2-letter ISO country code of residence. Must be one of the allowed countries (NL, BE, DE)")
    id_document: str = Field(..., description="Government-issued ID number, e.g., passport number")
    username: str = Field(..., min_length=3, max_length=20, description="Unique username for login (3~20 characters)")

# customer table
class Customer(CustomerBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    password: str
    accounts: list["Account"] = Relationship(back_populates="customer")
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))