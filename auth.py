from datetime import timedelta, datetime, timezone
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from sqlmodel import Session, select
from db import get_session
from models import Customer
from config import settings


def create_access_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode = {"sub": username, "exp": expire}
    token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return token

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/logon")

def get_current_customer(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> Customer:
    payload = decode_access_token(token)
    username = payload.get("sub")
    customer = session.exec(select(Customer).where(Customer.username == username)).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
