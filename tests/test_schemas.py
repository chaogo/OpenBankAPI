import pytest
from decimal import Decimal
from schemas.customer import CustomerCreate
from models.account import AccountBase


def test_dob_validator_rejects_underage():
    """Customer must be at least 18 years old."""
    with pytest.raises(ValueError, match="Customer must be at least 18 years old"):
        CustomerCreate(
            name="Young User",
            dob="2020-06-23",
            address="123 Street",
            country="NL",
            id_document="ID123456",
            username="younguser"
        )

def test_balance_validator_rejects_negative():
    """Balance must not be negative."""
    with pytest.raises(ValueError, match="Balance cannot be negative"):
        AccountBase(
            iban="NL00BANK1234567890",
            account_type="checking",
            balance=Decimal("-100.00"),
            currency="EUR"
        )

def test_balance_validator_normalizes_two_decimals():
    """Balance should be rounded/normalized to two decimals."""
    account = AccountBase(
        iban="NL00BANK1234567890",
        account_type="checking",
        balance=Decimal("123.4567"),
        currency="EUR"
    )
    assert account.balance == Decimal("123.46")