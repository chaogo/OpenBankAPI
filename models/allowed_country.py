from sqlmodel import SQLModel, Field

# allowed_countries table
class AllowedCountry(SQLModel, table=True):
    iso_code: str = Field(primary_key=True, min_length=2, max_length=2,
                          description="2-letter ISO country code allowed for registration")