import pytest
from httpx import AsyncClient, ASGITransport
from faker import Faker
from main import app
from models import Customer
from db import get_session
from utils import generate_password

fake = Faker()

@pytest.mark.asyncio
async def test_logon_success(monkeypatch):
    """Test successful login returns JWT token."""
    # First, create a user in DB via session
    username = fake.user_name()[:20]
    password = generate_password()
    # Insert into DB directly via session
    with next(get_session()) as session:
        customer = Customer(
            name=fake.name(),
            dob=fake.date_of_birth(minimum_age=18, maximum_age=70),
            address=fake.address(),
            country="NL",
            id_document=fake.bothify(text="ID#######"),
            username=username,
            password=password
        )
        session.add(customer)
        session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Use form data as OAuth2PasswordRequestForm expects
        response = await ac.post(
            "/auth/logon",
            data={"username": username, "password": password}
        )

    assert response.status_code == 200
    data = response.json()
    # Check presence of token and message
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["message"] == "Logon successful"


@pytest.mark.asyncio
async def test_logon_invalid_password(monkeypatch):
    """Test that wrong password returns 401."""
    # Set up a user
    username = fake.user_name()[:20]
    password = generate_password()
    with next(get_session()) as session:
        customer = Customer(
            name=fake.name(),
            dob=fake.date_of_birth(minimum_age=18, maximum_age=70),
            address=fake.address(),
            country="NL",
            id_document=fake.bothify(text="ID#######"),
            username=username,
            password=password
        )
        session.add(customer)
        session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/auth/logon",
            data={"username": username, "password": "wrongpass"}
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


@pytest.mark.asyncio
async def test_logon_nonexistent_user():
    """Login with non-existing username returns 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/auth/logon",
            data={"username": "doesnotexist", "password": "whatever"}
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"