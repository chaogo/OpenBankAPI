import random
import string
import secrets


def _iban_check_digits(country_code: str, bban: str) -> str:
    """Compute IBAN check digits using MOD-97-10.
    This is a simplified helper suitable for demo/testing purposes.
    """
    # Move country code and placeholder check digits to the end
    rearranged = bban + country_code + "00"
    # Convert letters to numbers (A=10, B=11, ..., Z=35)
    numeric = "".join(str(ord(ch) - 55) if ch.isalpha() else ch for ch in rearranged)
    # Compute mod 97
    remainder = 0
    for ch in numeric:
        remainder = (remainder * 10 + int(ch)) % 97
    check_digits = 98 - remainder
    return f"{check_digits:02d}"


def generate_iban(country_code: str = "NL") -> str:
    """Generate a pseudo-random IBAN.

    Notes:
    - This function focuses on NL IBAN format for simplicity:
      NLkk BBBB CCCCCCCCCC where:
        - kk: check digits
        - BBBB: bank code (4 letters)
        - CCCCCCCCCC: 10 digits account number
    - For other country codes, it will still return an NL-style IBAN with the requested country prefix.
    """
    country_code = (country_code or "NL").upper()
    bank_code = "".join(random.choice(string.ascii_uppercase) for _ in range(4))
    account_number = "".join(random.choice(string.digits) for _ in range(10))
    bban = f"{bank_code}{account_number}"
    check = _iban_check_digits(country_code, bban)
    return f"{country_code}{check}{bban}"


def generate_password(length: int = 12) -> str:
    """Generate a secure random password.

    Ensures the password contains at least one lowercase, one uppercase, and one digit.
    """
    if length < 8:
        length = 8  # enforce a sensible minimum

    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"

    while True:
        pwd = "".join(secrets.choice(alphabet) for _ in range(length))
        if any(c.islower() for c in pwd) and any(c.isupper() for c in pwd) and any(c.isdigit() for c in pwd):
            return pwd
