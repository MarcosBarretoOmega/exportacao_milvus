import sys

from dotenv import load_dotenv

from env_keys import get_env
from env_keys import USER_PASS
from env_keys import USER_EMAIL

if not load_dotenv("../.env"):
    load_dotenv(".env")

if not get_env(USER_EMAIL) or not get_env(USER_PASS):
    print("E-mail and Password must be at .env...")
    sys.exit()

from controller.controller import Controller

if not Controller().run():
    print("Something went wrong...")
    sys.exit()

print("_ ▮ !! >> Success << !! ▮ _")