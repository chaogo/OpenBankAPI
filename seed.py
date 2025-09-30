from faker import Faker
from sqlmodel import Session
from db import engine
from models import Customer, Account
from utils import generate_iban, generate_password
from decimal import Decimal
from random import choice

fake = Faker()

def seed(n: int = 10):
    with Session(engine) as session:
        # Create customers
        for _ in range(n):
            customer = Customer(
                name=fake.name(),
                dob=fake.date_of_birth(minimum_age=18, maximum_age=70),
                address=fake.address(),
                country=choice(["NL", "BE", "DE"]),
                id_document=fake.bothify(text="ID#######"),
                username=fake.user_name(),
                password=generate_password()
            )
            session.add(customer)

            # Each customer gets 1–2 accounts
            for _ in range(fake.random_int(min=1, max=2)):
                account = Account(
                    iban=generate_iban(),
                    account_type=choice(["checking", "saving", "investment"]),
                    currency=choice(["EUR", "GBP", "USD", "CAN", "CNY"]),
                    balance=Decimal(fake.random_number(digits=4)) / 100
                )
                customer.accounts.append(account)
                session.add(account)

        session.commit()
        print("Database seeded with sample data")

if __name__ == "__main__":
    seed()