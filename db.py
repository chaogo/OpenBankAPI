from sqlmodel import SQLModel, create_engine, Session, select

from models import AllowedCountry

DATABASE_URL = "sqlite:///bank.sqlite"
engine = create_engine(DATABASE_URL, echo=True)

def insert_allowed_countries(session: Session):
    initial_allowed_countries = ["NL", "BE", "DE"]
    for country in initial_allowed_countries:
        if not session.get(AllowedCountry, country):
            session.add(AllowedCountry(iso_code=country))
    session.commit()

def init_db():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        insert_allowed_countries(session)

def get_session():
    with Session(engine) as session:
        yield session