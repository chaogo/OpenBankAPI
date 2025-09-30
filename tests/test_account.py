import pytest
from httpx import AsyncClient, ASGITransport
from faker import Faker
from main import app


fake = Faker()

async def register_and_logon(ac: AsyncClient):
    """Helper: register a user and return (username, token)."""
    username = fake.user_name()[:20]
    payload = {
        "name": fake.name(),
        "dob": fake.date_of_birth(minimum_age=18, maximum_age=70).isoformat(),
        "address": fake.address(),
        "country": "NL",
        "id_document": fake.bothify(text="ID#######"),
        "username": username,
    }

    # Register
    resp = await ac.post("/customers/register", json=payload)
    assert resp.status_code == 201
    password = resp.json()["password"]

    # Logon
    resp = await ac.post(
        "/auth/logon",
        data={"username": username, "password": password}
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    return username, token


@pytest.mark.asyncio
async def test_open_account_success():
    """Customer can open a new account with valid JWT."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        _, token = await register_and_logon(ac)

        resp = await ac.post(
            "/accounts/open",
            headers={"Authorization": f"Bearer {token}"},
            json={"account_type": "saving", "currency": "EUR"}
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["account_type"] == "saving"
        assert data["currency"] == "EUR"


@pytest.mark.asyncio
async def test_open_account_unauthorized():
    """Opening an account without token should fail."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post(
            "/accounts/open",
            json={"account_type": "checking", "currency": "EUR"}
        )
        assert resp.status_code == 401


@pytest.mark.asyncio
async def test_overview_returns_accounts():
    """Overview should list all customer accounts with valid JWT."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        _, token = await register_and_logon(ac)

        # Open two accounts
        for acc_type in ["checking", "investment"]:
            await ac.post(
                "/accounts/open",
                headers={"Authorization": f"Bearer {token}"},
                json={"account_type": acc_type, "currency": "EUR"}
            )

        resp = await ac.get(
            "/accounts/overview",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200
        accounts = resp.json()["accounts"]
        assert len(accounts) >= 2
        account_types = [a["account_type"] for a in accounts]
        assert "checking" in account_types
        assert "investment" in account_types


@pytest.mark.asyncio
async def test_overview_unauthorized():
    """Overview without token should return 401 Unauthorized."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/accounts/overview")
        assert resp.status_code == 401


@pytest.mark.asyncio
async def test_invalid_token_rejected():
    """Requests with invalid token should return 401 Unauthorized."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get(
            "/accounts/overview",
            headers={"Authorization": "Bearer faketoken123"}
        )
        assert resp.status_code == 401