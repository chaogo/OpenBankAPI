from pydantic import BaseModel, Field
from models import AccountType, AccountBase


class AccountRequest(BaseModel):
    account_type: AccountType = Field(...)
    currency: str = Field("EUR", min_length=3, max_length=3, description="Currency code (ISO 4217, e.g., EUR, USD)")

# account properties to response to the customer
class AccountPublic(AccountBase):
    pass

class AccountsResponse(BaseModel):
    message: str
    accounts: list[AccountPublic]