import os
import hmac
from dotenv import load_dotenv

load_dotenv()


def get_credentials() -> tuple[str, str]:
    username = os.getenv("APP_USERNAME", "admin")
    password = os.getenv("APP_PASSWORD", "changeme")
    return username, password


def verify_credentials(username: str, password: str) -> bool:
    expected_user, expected_pass = get_credentials()
    user_ok = hmac.compare_digest(username, expected_user)
    pass_ok = hmac.compare_digest(password, expected_pass)
    return user_ok and pass_ok
