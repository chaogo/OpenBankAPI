# OpenBankAPI

A lightweight banking API that provides customer registration, logon, and account overview features.

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

- API base URL → http://127.0.0.1:8000
- Swagger UI (OpenAPI docs) → http://127.0.0.1:8000/docs
- ReDoc → http://127.0.0.1:8000/redoc

## 🏗️ Design

### Tech Stack
- **FastAPI**: with Pydantic, Uvicorn
- **SQLite**
- **SQLAlchemy**

### Data Model
#### ER Diagram
```
+-------------+         +-------------+
|   Customer  | 1     * |   Account   |
+-------------+         +-------------+
| id          |---------| id          |
| username    |         | customer_id |
| password    |         | iban        |
| name        |         | account_type|
| dob         |         | balance     |
| address     |         | currency    |
| country     |         | created_at  |
| id_document |         +-------------+
| created_at  |         
+-------------+

+-----------------+
| AllowedCountry  |
+-----------------+
| id              |
| iso_code        |
+-----------------+
```

#### Customer Table
| Field       | Type         | Constraints / Notes                     |
|-------------|--------------|-----------------------------------------|
| id          | UUID         | Primary key                             |
| username    | VARCHAR(50)  | Unique, required                        |
| password    | VARCHAR(255) | Plaintext                               |
| name        | VARCHAR(100) | Customer full name                      |
| dob         | DATE         | Must be ≥18 years old                   |
| address     | VARCHAR(255) | Free text address                       |
| country     | CHAR(2)      | Must exist in AllowedCountry (ISO code) |
| id_document | VARCHAR(50)  | Abstracted as a simple document number  |
| created_at  | TIMESTAMP    | Customer registration timestamp         |

#### Account Table
| Field        | Type          | Constraints / Notes              |
|--------------|---------------|----------------------------------|
| id           | UUID          | Primary key                      |
| customer_id  | UUID          | Foreign key → Customer.id        |
| iban         | CHAR(18)      | Unique, generated as per NL IBAN |
| account_type | VARCHAR(20)   | e.g. “savings”, “checking”       |
| balance      | DECIMAL(15,2) | Default 0.00                     |
| currency     | CHAR(3)       | ISO currency code (e.g., EUR)    |
| created_at   | TIMESTAMP     | Account opening timestamp        |

#### AllowedCountry Table
A separate table for allowed countries is created to make it easy to maintain and extend.

| Field    | Type    | Constraints / Notes                                     |
|----------|---------|---------------------------------------------------------|
| id       | INT     | Primary key                                             |
| iso_code | CHAR(2) | Unique, ISO 3166-1 alpha-2 country code (NL, BE, DE, …) |


### Request Flow
#### /register Flow
```
Client         FastAPI        Service Layer       SQLAlchemy ORM     Database
   |               |                |                  |               |
   | POST /register|                |                  |               |
   |-------------->|                |                  |               |
   |   JSON body   |                |                  |               |
   |               | Validate schema|                  |               |
   |               |--------------->|                  |               |
   |               |   valid data   |                  |               |
   |               |                | Business rules   |               |
   |               |                | - check age ≥18  |               |
   |               |                | - check country  |               |
   |               |                | - unique username|               |
   |               |                | - generate IBAN  |               |
   |               |                | - generate pwd   |               |
   |               |                |----------------->|               |
   |               |                |   insert rows    |-------------->|
   |               |                |                  |   persist     |
   |               |                |<-----------------|               |
   |               |<---------------|                  |               |
   |   200 JSON    |                |                  |               |
   |<--------------|                |                  |               |

```

#### /logon Flow

#### /overview Flow

### Design Trade-offs
- **ID Document**: Simplified to a string field
- **Password**: Plaintext
- **IBAN Generation**: Simplified to `NL{random2}{BANK}{random10digits}`
- **Authentication**: Simply logon with username+password
- **Database Migration**: No migration tooling like Alembic is used


## 📖 Reflection
- This project gives me a big motivation to refresh my Python, backend dev in general, 
- and excited to pick up new tools and framework like uv, pydantic, etc.
- more reflection along with building

