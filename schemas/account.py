from pydantic import BaseModel, Field
from models import AccountType, AccountBase


class AccountRequest(BaseModel):
    account_type: AccountType = Field(...)

# account properties to response to the customer
class AccountPublic(AccountBase):
    pass

class AccountsResponse(BaseModel):
    message: str
    accounts: list[AccountPublic]