from os import environ

USER_EMAIL: str = "USER_EMAIL_LOGIN"
USER_PASS: str = "USER_PASS_LOGIN"
TOKEN_API_CLIENT: str = "TOKEN_API_CLIENT"

def get_env(key: str) -> str | None:
    return environ.get(key)