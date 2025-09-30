from .customer import router as customer_router
from .auth import router as auth_router
from .account import router as account_router

__all__ = ["customer_router", "auth_router", "account_router"]