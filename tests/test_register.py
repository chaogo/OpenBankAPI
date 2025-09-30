import pytest
from httpx import AsyncClient, ASGITransport
from faker import Faker
from main import app


fake = Faker()

@pytest.mark.asyncio
async def test_register_success():
    """Successful customer registration should return 201 and credentials."""
    payload = {
        "name": fake.name(),
        "dob": fake.date_of_birth(minimum_age=18, maximum_age=70).isoformat(),
        "address": fake.address(),
        "country": "NL",  # must be in AllowedCountry
        "id_document": fake.bothify(text="ID#######"),
        "username": fake.user_name()[:20],  # ensure within schema length
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/customers/register", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == payload["username"]


@pytest.mark.asyncio
async def test_register_duplicate_username():
    """Registering the same username twice should fail with 409 Conflict."""
    username = fake.user_name()[:20]

    payload = {
        "name": fake.name(),
        "dob": fake.date_of_birth(minimum_age=18, maximum_age=70).isoformat(),
        "address": fake.address(),
        "country": "NL",
        "id_document": fake.bothify(text="ID#######"),
        "username": username,
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # First attempt → should succeed
        response1 = await ac.post("/customers/register", json=payload)
        assert response1.status_code == 201

        # Second attempt → should fail
        response2 = await ac.post("/customers/register", json=payload)
        assert response2.status_code == 409
        assert response2.json()["detail"] == "Username already exists"


@pytest.mark.asyncio
async def test_register_disallowed_country():
    """Registration should fail if country is not in AllowedCountry."""
    payload = {
        "name": fake.name(),
        "dob": fake.date_of_birth(minimum_age=18, maximum_age=70).isoformat(),
        "address": fake.address(),
        "country": "XX",  # not in the allowedcountry table
        "id_document": fake.bothify(text="ID#######"),
        "username": fake.user_name()[:20],
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/customers/register", json=payload)

    assert response.status_code == 403
    assert response.json()["detail"] == "Registration not allowed from this country"