from datetime import date
from pydantic import field_validator
from models import CustomerBase


# Properties to receive via /register endpoint
class CustomerCreate(CustomerBase):
    @field_validator("dob")
    def validate_dob(cls, v: date):
        age = (date.today() - v).days // 365
        if age < 18:
            raise ValueError("Customer must be at least 18 years old")
        return v