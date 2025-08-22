import os
from io import StringIO

from typing import Any

from json import loads
from json import dumps as from_json

from web.web import Web

from env_keys import get_env
from env_keys import USER_PASS
from env_keys import USER_EMAIL

LIMIT_ATTEMPT: int = 5

FILE_CLIENT_MAP: str = "../clients.txt"
FILE_PASSWORD_MAP: str = "../passwords.txt"
FILE_PASSWORD_VAULT_MAP: str = "../password-vaults.txt"

def dumps(obj: Any) -> str:
    return from_json(obj, ensure_ascii=False)

class Controller:
    def __init__(self) -> None:
        self.web: Web = Web(
            user=get_env(USER_EMAIL),
            password=get_env(USER_PASS)
        )
        self.token: str | None = None

    def set_token(self, ignore: bool = False) -> bool:
        if ignore:
            return True

        if self.token:
            return self.token

        self.token = self.web.get_acess_token()

        if not self.token:
            return False

        return True

    def save_file(self, path_file: str, content: str | bytes | None = None) -> bool:
        try:
            with open(path_file, "wb") as file:
                if isinstance(content, bytes):
                    file.write(content)

                elif isinstance(content, str):
                    file.write(content.encode())

                file.close()

        except Exception as e:
            print(f"-- erro: {str(e)}")
            return False

        return True

    def load_file(self, path_file: str) -> str | None:
        if not os.path.isfile(path_file):
            return None

        file_content: str = ""
        try:
            with open(path_file, "rb") as file:
                file_content = file.read().decode()
                file.close()

        except Exception as e:
            print(f"-- erro: {str(e)}")
            return None

        if not file_content:
            return None

        return file_content

    def save_client_at_file(self, override: bool = False) -> bool:
        if not override and os.path.isfile(FILE_CLIENT_MAP):
            return True

        clients: list[dict] = self.web.get_clients()

        if not clients:
            return False

        return self.save_file(path_file=FILE_CLIENT_MAP, content=dumps(clients))

    def save_password_vault_at_file(self, override: bool = False) -> bool:
        if not override and os.path.isfile(FILE_PASSWORD_VAULT_MAP):
            return True

        password_vault: list[dict] = self.web.get_password_vault()
        if not password_vault:
            return False

        return self.save_file(path_file=FILE_PASSWORD_VAULT_MAP, content=dumps(password_vault))

    def get_password_vaults(self) -> list[dict]:
        file_content: str | None = self.load_file(FILE_PASSWORD_VAULT_MAP)

        if not file_content:
            return []

        return loads(file_content)

    def get_clients(self) -> list[dict]:
        file_content: str | None = self.load_file(FILE_CLIENT_MAP)

        if not file_content:
            return []

        return loads(file_content)

    def get_save_password_map(self) -> dict:
        file_content: str | None = self.load_file(FILE_PASSWORD_MAP)
        if not file_content:
            return {}

        return loads("{%s}" % file_content[:len(file_content) - 3].replace("\n", ""))

    def get_colunm_value(self, data: dict, colunm_name: str) -> Any:
        for item in data:
            if not data[item].get(colunm_name):
                yield ""

            yield data[item][colunm_name]

    def build_sheet(self) -> bool:
        senhas: dict = self.get_save_password_map()
        print([_ for _ in self.get_colunm_value(senhas, "description")])
        import pdb;pdb.set_trace()

    def list_to_hash_by_field(self, data: list[dict], field: str) -> dict:
        if not isinstance(data, list) or not isinstance(field, str):
            return {}

        result: dict = {}
        for item in data:
            if not isinstance(item, dict):
                continue

            if not item.get(field):
                continue

            if result.get(item[field]):
                continue

            result[item[field]] = item

        return result

    def save_password_map_at_file(self, override: bool = False) -> bool:
        clients_cache: dict = self.list_to_hash_by_field(self.get_clients(), "id")
        passwords_vault_cache: dict = self.list_to_hash_by_field(self.get_password_vaults(), "id")

        attemp_count: int = 0
        try:
            saved_passwords: dict[dict] = self.get_save_password_map()

            try:
                with open(FILE_PASSWORD_MAP, "ab+") as file:
                    for password_vault in passwords_vault_cache:
                        if attemp_count >= LIMIT_ATTEMPT:
                            raise Exception("max attemps!")

                        if saved_passwords.get(str(password_vault)):
                            print(f"--- info: duplicate pass {password_vault}, ignoring...\n")
                            continue

                        req_password: str = self.web.get_password(password_vault)
                        password: dict = passwords_vault_cache[password_vault]
                        client: dict = clients_cache[password["cliente_id"]]

                        line: StringIO = StringIO()

                        line.write("\"%s\": " % str(password_vault))

                        line.write(
                           dumps(
                                {
                                    "description": password["descricao"],
                                    "user": password["usuario"],
                                    "obs": password["observacao"],
                                    "client": client["id"],
                                    "client_name": client["razao_social"],
                                    "create_date": password["data_criacao"],
                                    "password": req_password
                                }
                            )
                        )

                        line.write(", \n")

                        file.write(line.getvalue().encode())

                        line.close()

                    file.close()

            except Exception as e:
                import pdb;pdb.set_trace()
                raise Exception(f"-- erro: {str(e)}")

        except Exception as e:
            print(f"-- erro: {str(e)}")
            return False

        return True

    def run(self) -> bool:
        if not self.save_client_at_file():
            return False

        if not self.set_token(ignore=True):
            return False

        if not self.save_password_vault_at_file():
            return False

        if not self.save_password_map_at_file():
            return False

        if not self.build_sheet():
            return False

        return True
