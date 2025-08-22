from time import sleep

from json import loads

from http import HTTPStatus

from requests import get
from requests import post
from requests import Response

from env_keys import get_env
from env_keys import TOKEN_API_CLIENT

ROUTE_LOGIN: str = "https://managerapi.milvus.com.br/manager/accounts/v2/login"

ROUTE_API_CLIENT: str = "https://apiintegracao.milvus.com.br/api/cliente/busca"

BASE_ROUTE_API: str = "https://api.milvus.com.br/api"
ROUTE_API_GET_PASS: str = BASE_ROUTE_API + "/senhas/valida"
ROUTE_API_GET_PASSWORD_VAULT: str = BASE_ROUTE_API + "/senhas/list?is_paginate=false"

SLEEP_TIME_REQUEST_SECS: int = 1

def sleep_request(func=None):
    def wrapper(*args, **kwargs):
        count: int = SLEEP_TIME_REQUEST_SECS - 1

        print("--- WEB - REQUEST")
        print(f"-- {func.__name__}: - info: init..")

        ret = func(*args, **kwargs)

        while True:
            print(f"--- wait: {str(count)}...")
            count -= 1
            sleep(1)

            if count < 1:
                break

        print(f"-- {func.__name__}: - info: end..")
        print("")

        return ret

    return wrapper

class Web:
    def __init__(self, user: str, password: str) -> None:
        self.user: str = user
        self.password: str = password
        self.__token: str | None = None

    def __get_response_result(self, response: Response) -> dict:
        try:
            result: dict = loads(response.content.decode(encoding="utf-8"))
            return result

        except Exception as e:
            print(f" -- erro: {str(e)}")

    def get_acess_token(self) -> str | None:
        try:
            if self.__token:
                return self.__token

            form_login: dict = {
                "email": self.user,
                "password": self.password
            }

            request: Response = post(
                url=ROUTE_LOGIN,
                data=form_login
            )

            result: dict = self.__get_response_result(request)

            if not HTTPStatus(request.status_code).is_success:
                raise Exception(result.get("message"))

            if not result.get("AuthenticationResult", {}).get("AccessToken"):
                raise Exception("Not possible to get token")

            self.__token = result["AuthenticationResult"]["AccessToken"]

            return self.__token

        except Exception as e:
            print(f"-- token: - erro: {str(e)}")
            return ""

    @sleep_request
    def get_clients(self) -> list[dict]:
        try:
            if not get_env(TOKEN_API_CLIENT):
                raise Exception(f"Pls, check at .env, if '{TOKEN_API_CLIENT}' are empty.")

            request: Response = get(
                url=ROUTE_API_CLIENT,
                headers={
                    "Authorization": get_env(TOKEN_API_CLIENT)
                }
            )

            result: dict = self.__get_response_result(request)

            if not HTTPStatus(request.status_code).is_success:
                raise Exception(result.get("message"))

            if not result.get("lista"):
                raise Exception("Invalid client list")

            return result["lista"] or []

        except Exception as e:
            print(f"-- clients: - erro: {str(e)}")
            return []

    @sleep_request
    def get_password_vault(self) -> list[dict]:
        try:
            request: Response = post(
                url=ROUTE_API_GET_PASSWORD_VAULT,
                headers={
                    "Authorization": self.get_acess_token()
                }
            )

            result: dict = self.__get_response_result(request)

            if not HTTPStatus(request.status_code).is_success:
                raise Exception(result.get("message"))

            if not result.get("lista"):
                raise Exception("Not possible to get this list")

            return result["lista"]

        except Exception as e:
            print(f"-- password vault: - erro: {str(e)}")
            return ""

    @sleep_request
    def get_password(self, password_id: int) -> str | None:
        try:
            if not isinstance(password_id, int):
                raise Exception("Invalid pass ID")

            json_body: dict = {
                "username": self.user,
                "senha_id": password_id,
                "senha": self.password
            }

            request: Response = post(
                url=ROUTE_API_GET_PASS,
                data=json_body,
                headers={
                    "Authorization": self.get_acess_token()
                }
            )

            if not HTTPStatus(request.status_code).is_success:
                raise Exception(request.json().get("message"))

            result: dict = request.json()

            if not result.get("senha"):
                raise Exception("Not possible to get this pass")

            return result["senha"]

        except Exception as e:
            print(f"-- password: - erro: {str(e)}")
            return ""
