import pandas as pd
from typing import Hashable
from numpy import isnan

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


def check_organization(value: str) -> bool:
    """

    :param value:
    :return: return False if wrong organization name
    """

    if_cor_type = False
    for org_type in ORGANIZATION_TYPES:
        if org_type in value:
            return True
    return False


def check_float(candidate):
    try:
        print(f"{candidate=} {float(candidate)=} {isnan(float(candidate))=}")
        if isnan(float(candidate)):
            return False
        float(candidate)
        return True
    except ValueError:
        return False
    except TypeError:
        return False


def validate(dataframe: pd.DataFrame) -> list[Hashable]:
    """
    :param dataframe: column: "Значение"
    :return:
    """
    unvalidated: list[Hashable] = []
    col_name = "Значение"
    for index, row in dataframe.iterrows():
        value = row[col_name]
        if index == "Организация":
            if not check_organization(value):
                unvalidated.append(index)
        elif index == "Тип формы":
            if "Типовая межотраслевая форма" not in value:
                unvalidated.append(index)
        elif index == "Требование-накладная":
            if not check_float(value):
                unvalidated.append(index)
        elif "Коды" in index:
            if not check_float(value):
                unvalidated.append(index)

        elif "документ" in index.lower():

            if not check_float(value):
                unvalidated.append(index)
            elif float(value) <= 0:
                unvalidated.append(index)
        else:
            try:
                if len(value.split(" ")) < 3:
                    unvalidated.append(index)
            except AttributeError:
                # if not str
                unvalidated.append(index)

    return unvalidated


if __name__ == '__main__':
    df = pd.read_csv('src/report.csv', index_col=0)
    print(validate(df))
