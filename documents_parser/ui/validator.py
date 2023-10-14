import pandas as pd
from typing import Hashable

ORGANIZATION_TYPES = [
    "ОАО",
    "ООО",
    "ЗАО",
    "ПАО",
    "НКО",
    "ГК",
    "АО",
    "ТСЖ",
    "КФХ",
    "ИП",
    "АНО",
    "НП",
    "ОП",
    "ФГУП",
    "ФСК",
    "ФСБ",
    "ФСС",
    "ФСТЭК"
]

def check_organization():

def validate(dataframe: pd.DataFrame) -> list[Hashable]:
    """
    :param dataframe: column: "Значение"
    :return:
    """
    unvalidated: list[Hashable] = []
    col_name = "Значение"
    # print(dataframe)
    for index, row in dataframe.iterrows():
        value = row[col_name]
        if index == "Организация":
            if "\"" not in value:
                unvalidated.append(index)
            elif



    return unvalidated

if __name__ == '__main__':
    df = pd.read_csv('src/report.csv', index_col=0)
    print(validate(df))