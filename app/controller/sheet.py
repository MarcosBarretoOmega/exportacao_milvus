import os
import pandas as pd

class Sheet:
    @classmethod
    def create_excel(cls, file_name: str, data_frame: dict, sheet_name: str) -> bool:
        if not isinstance(data_frame, dict):
            return False

        path_file: str = os.path.join(os.getcwd(), file_name + ".xlsx")

        if not os.path.exists(path_file) or not os.path.isfile(path_file):
            with open(path_file, "w") as file:
                file.write("")
                file.close()

        try:
            pd.DataFrame(data=data_frame).to_excel(path_file, sheet_name=sheet_name, index=False)

            return True

        except Exception as e:
            print(f"-- erro: {str(e)}")
            return False
