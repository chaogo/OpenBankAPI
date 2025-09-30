from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, select
from routers import account_router, auth_router, customer_router
from models import AllowedCountry
from contextlib import asynccontextmanager
from db import init_db, get_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()          # Startup
    yield
    print("Goodbye!")  # Shutdown

app = FastAPI(lifespan=lifespan)

@app.get(
    "/",
    tags=["General"],
    summary="Home page",
    description="Welcome endpoint providing a simple landing message and docs link."
)
async def root():
    return {
        "message": "Welcome to OpenBankAPI ;)",
        "docs": "/docs",
    }

@app.get(
    "/health",
    tags=["Monitoring"],
    summary="Health check",
    description="Checks service and database availability",
    responses={
        200: {"description": "Service and database are healthy"},
        503: {"description": "Database is unavailable"}
    }
)
async def healthcheck(session: Session = Depends(get_session)):
    try:
        session.exec(select(AllowedCountry)).first()
        return {"status": "ok", "database": "connected"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")

app.include_router(customer_router)
app.include_router(auth_router)
app.include_router(account_router)
