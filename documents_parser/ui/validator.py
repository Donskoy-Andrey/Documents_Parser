import pandas as pd
from typing import Hashable, Tuple, Any
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


def check_float(candidate: Any) -> bool:
    """
    :param candidate:
    :return: True if the candidate can be float
    """
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


def validate(dataframe: pd.DataFrame) -> Tuple[list[Hashable], list[str]]:
    """

    :param dataframe: column: "Значение"
    :return: list of indexes with wrong col, list of reasons
    """
    unvalidated: list[Hashable] = []
    reasons: list[str] = []
    col_name = "Значение"
    for index, row in dataframe.iterrows():
        value = row[col_name]
        if index == "Организация":
            if not check_organization(value):
                unvalidated.append(index)
                reasons.append("Неверное название организации")
        elif index == "Тип формы":
            if "Типовая межотраслевая форма" not in value:
                unvalidated.append(index)
                reasons.append("Отсутствует фраза: \"Типовая межотраслевая форма\"")
        elif index == "Требование-накладная":
            if not check_float(value):
                unvalidated.append(index)
                reasons.append(f"Требование-накладная: Неверный формат номера (только числа)")
        elif "Коды" in index:
            if not check_float(value):
                unvalidated.append(index)
                reasons.append(f"{index}: Неверный формат номера (только числа)")

        elif "документ" in index.lower():

            if not check_float(value):
                unvalidated.append(index)
                reasons.append(f"{index}: Неверный формат номера (только числа)")
            elif float(value) <= 0:
                unvalidated.append(index)
                reasons.append(f"{index}: Неверный формат номера (только числа > 0)")
        else:
            try:
                if len(value.split(" ")) < 3:
                    unvalidated.append(index)
                    reasons.append(f"{index}: Неверный формат")
            except AttributeError:
                # if not str
                unvalidated.append(index)
                reasons.append(f"{index}: Неверный формат")

    return unvalidated, reasons


if __name__ == '__main__':
    df = pd.read_csv('src/report.csv', index_col=0)
    print(validate(df))
