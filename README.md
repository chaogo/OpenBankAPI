# OpenBankAPI

A lightweight banking API that provides customer registration, logon, open account, and account overview features.

## 🚀 Getting Started

### Prerequisites

This project uses [uv](https://docs.astral.sh/uv/getting-started/installation/) for dependency and environment management.

### Setup

```Bash
# Install dependencies from pyproject.toml
uv sync
```

### Run
```Bash
uv run uvicorn main:app
```

### Test
- Health check
    ```Bash
    curl http://127.0.0.1:8000/health
    ```
- Automated test using pytest with coverage
    ```Bash
    pytest
    ```
- Populate the database with sample data for easier manual testing
    ```Bash
    uv run python seed.py
    ```
- Interactive testing using Postman collection: `OpenBankAPI.postman_collection.json`

### API documentation
- Swagger UI → http://127.0.0.1:8000/docs
- ReDoc → http://127.0.0.1:8000/redoc

## 🏗️ Design
Although it’s a small project, my goal was to make it correct, clean, and complete.
- Correct and clean can be achieved along the way by careful coding and structure.
- Complete requires more design thinking and trade-offs, especially since the assignment leaves space for interpretation.

### Tech Stack
Since this is a demo project requiring fast development
- SQLite was the natural database choice — it’s lightweight and avoids setup overhead. 
- Python was chosen for its simplicity and ease of use, plus SQLite is built-in.
- FastAPI was chosen as Python was chosen, plus I had a little prior experience using Flask in another personal project.

### Business Interpretation
The specification left some gaps. For example:
- /register requires address, ID document, and country, but doesn’t specify which field should determine the customer’s country.
- /logon only expects a success response, making it more like a credential check than a real login process.
- /overview should give a customer overview. It’s intuitive that a customer might have multiple accounts, but there’s no explicit endpoint to create accounts, and it’s unclear if an account needs to be created automatically when a customer registers.
- It should be possible to add new countries to the allowed list "easily".

Here is my interpretation:
- /register uses the country field to validate if registration is allowed.
- /logon issues a JWT token when credentials are correct, so customers don’t need to re-enter credentials every time.
- One customer can hold multiple accounts, so an extra endpoint /accounts/open is added.
- A dedicated table for allowed countries is created for flexibility.

### Technical Trade-offs
- In a real bank, an **ID document** would need to be uploaded and verified against other information, including the allowed country. Here, it’s simplified as a plain string field of ID number.
- Database migrations (Alembic) are skipped to keep things lightweight; instead, the schema is reset when needed.
- Database error handling is minimal to keep it simple — e.g. integrity errors are not mapped in detail, and DB failure is not mocked.

### Future Improvements
- **Refresh tokens** to support longer and more secure user sessions.
- **bcrypt password hashing** instead of storing plaintext passwords.
- **Admin role** to manage allowed countries, and supported currencies.
- Business rules such as preventing duplicate account types per customer.


## 📖 Reflection
This project gave me strong motivation to strengthen my Python and backend development skills. 
I really enjoyed the cycle of analyzing, designing, learning, implementing, and refining on a project of my own. 
One highlight was to quickly pick up new tools and apply them directly in the project — such as FastAPI, Pydantic, uv, pytest, and Faker. 
That’s also why I tried to write down detailed commits and messages, to clearly show how the project evolved from scratch.

I also gained valuable experience working with GPT as a mentor-like assistant. It gave me quick help by:
- Broadening my view with tools and libraries I hadn’t considered, e.g., Faker for sample test data
- Clarifying unfamiliar syntax and semantics, such as forward references with SQLModel
- Suggesting architectural improvements, like restructuring into models/, schemas/, and routers/ packages, and introducing .env configs.
- Assisting with utility functions (e.g. generating IBANs, generating secure passwords), so I could focus on business logic while still reviewing and testing helper code.
- Sharing domain knowledge, such as IBAN format, ISO country codes, etc.

Meanwhile, GPT doesn’t always provide the most optimal or up-to-date approach. 
It often suggests the most common way (sometimes older or deprecated practices), and I had to guide it toward newer alternatives — for example:
- `@app.on_event("startup")` vs. the modern **lifespan** event handler.
- `session.query()` vs. `session.exec(select(...))`.
- 
It also didn’t fully solve data schema redundancy issues, which I later learned about through the official FastAPI templates.
From this, I learned that the best approach might be a combination: following structured courses for comprehensive understanding, while using AI tools for quick help and idea exploration.

Acknowledge to courses that helped shape this project (also kept here for future reference):
- [FastAPI - Complete Course for Python API Development](https://www.youtube.com/playlist?list=PL-2EBeDYMIbTJrr9qaedn3K_5oe0l4krY)
- [Overview of FastAPI](https://hyperskill.org/learn/step/52311)
- [Python FastAPI Tutorial: Build a REST API in 15 Minutes](https://youtu.be/iWS9ogMPOI0?si=UxceMv_ly8rZaZN5)
- [Pydantic Tutorial • Solving Python's Biggest Problem](https://youtu.be/XIdQ6gO3Anc?si=v_nK_C_mBCC_90mU)
- [UV: The Python Tool Everyone Is Switching To](https://youtu.be/k0F9YaAbNwo?si=aUI2ETXtsWIl_QH2)
- [FastAPI JWT Authentication 2025](https://www.youtube.com/watch?v=I11jbMOCY0c)
- [PyTest • REST API Integration Testing with Python](https://youtu.be/7dgQRVqF1N0?si=Yy78ip0299Fi8oFL)