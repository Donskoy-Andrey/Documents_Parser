import pandas as pd
from typing import Hashable, Tuple, Any, Literal
from numpy import isnan
import datetime

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
        if isnan(float(candidate)):
            return False
        float(candidate)
        return True
    except ValueError:
        return False
    except TypeError:
        return False


def validate_raw_data_m11(dataframe: pd.DataFrame) -> Tuple[list[Hashable], list[str]]:
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


def identify_df(dataframe: pd.DataFrame) -> Literal[1, 2, 3]:
    # print(f"{dataframe.columns=}")
    if dataframe.columns[0] in ["Дата составления", "Дата\nсоставления"]:
        return 1
    elif dataframe.columns[0] in ["Корреспондирующий счет", "Корреспондирующий\nсчет"]:
        return 2
    return 3


def check_date(date: str) -> bool:
    day, month, year = date.split(".")
    try:
        if len(day) > 2 or int(day) < 1 or int(day) > 31:
            return False
        if len(month) > 2 or int(month) < 1 or int(month) > 12:
            return False
        if len(year) != 4 or int(year) > datetime.date.today().year:
            return False
        return True
    except AttributeError:
        # if cannot int()
        return False


def validate_dataframe_m11_1(dataframe: pd.DataFrame):
    reasons = []
    unvalidated = []

    for index, row in dataframe.iterrows():
        # print(f"{index=} {row=}")
        # validate date
        if not check_date(row["Дата составления"]):
            unvalidated.append((index, "Дата составления"))
            reasons.append("Неверная дата составления")
        # validate code
        if not row["Код вида операции"].isdigit():
            unvalidated.append((index, "Код вида операции"))
            reasons.append("Неверный код вида операции")
        # validate sender and receiver ==================================
        sender_fields = [row[col] for col in dataframe.columns if "Отправитель" in col]
        receiver_fields = [row[col] for col in dataframe.columns if "Получатель" in col]
        sender_info = False
        receiver_info = False
        for sender in sender_fields:
            if len(sender) > 10:
                sender_info = True
        for receiver in receiver_fields:
            if len(receiver) > 10:
                receiver_info = True
        if not sender_info:
            cols = [col for col in dataframe.columns if "Отправитель" in col]
            for col in cols:
                unvalidated.append((index, col))
            reasons.append("Нет данных об отправителе")
        if not receiver_info:
            cols = [col for col in dataframe.columns if "Получатель" in col]
            for col in cols:
                unvalidated.append((index, col))
            reasons.append("Нет данных об получателе")

        corresponding_account = [col for col in dataframe.columns if "Корреспондирующий счет" in col]
        for col in corresponding_account:
            if not row[col].replace(" ", "").isdigit() and row[col] != "-":
                unvalidated.append((index, col))
                reasons.append(f"{col}: неправильные данные")
            elif not row[col].startswith("7909"):
                unvalidated.append((index, col))
                reasons.append(f"{col}: неправильные данные (начинается с 7909)")

    return unvalidated, reasons


def validate_dataframe_m11_2(dataframe: pd.DataFrame):
    reasons = []
    unvalidated = []
    for index, row in dataframe.iterrows():
        if index == 2:
            continue
        corresponding_account = [col for col in dataframe.columns if "Корреспондирующий счет" in col]
        for col in corresponding_account:
            print("aaaa ", row[col])
            if (not row[col].replace(" ", "").replace("\n", "").isdigit()
                    and row[col] != "-"):
                unvalidated.append((index, col))
                reasons.append(f"{col}: неправильные данные (начинается с 1003)")
            elif not row[col].startswith("1003"):
                unvalidated.append((index, col))
                reasons.append(f"{col}: неправильные данные")

        if not row["Материальные ценности (номенклатурный номер)"].replace(" ", "").replace("\n", "").isdigit():
            unvalidated.append((index, "Материальные ценности (номенклатурный номер)"))
            reasons.append(f'"Материальные ценности (номенклатурный номер)": неправильные данные (только цифры)')
        if not row["Единица измерения (код)"].isdigit():
            unvalidated.append((index, "Единица измерения (код)"))
            reasons.append(f'"Единица измерения (код)": неправильные данные (только цифры)')
        totals = [col for col in dataframe.columns if "Количество" in col]
        for col in totals:
            if not check_float(row[col].replace(" ", "").replace("\n", "")):
                unvalidated.append((index, col))
                reasons.append(f"{col}: неправильные данные")
        prices = [col for col in dataframe.columns if "руб." in col]
        for col in prices:
            try:
                if len(row[col].replace("\n", "").replace(" ", "").split(",")) != 2:
                    print("aaaaaa ", row[col])
                    unvalidated.append((index, col))
                    reasons.append(f"{col}: Неправильный денежный формат (руб,коп)")
                else:
                    rub, kop = row[col].split(",")
                    rub = rub.replace(" ", "").replace("\n", "")
                    kop = kop.replace(" ", "").replace("\n", "")
                    print(f'{rub=} {rub.isdigit()=} {kop=} {kop.isdigit()=} {not rub.isdigit() or not kop.isdigit()}')
                    if not rub.isdigit() or not kop.isdigit():
                        print(f"{rub=} {rub.isdigit()=}")
                        unvalidated.append((index, col))
                        reasons.append(f"{col}: Неправильный денежный формат (руб,коп)")

            except AttributeError:
                print('here ', row[col])

                unvalidated.append((index, col))
                reasons.append(f"{col}: Неправильный денежный формат (руб,коп)")
    return unvalidated, reasons


def validate_tables_m11(dataframe: pd.DataFrame):
    # for dataframe in dataframes:
    df_type = identify_df(dataframe)
    # print(f"{df_type=}")
    if df_type == 1:
        return validate_dataframe_m11_1(dataframe)
    elif df_type == 2:
        return validate_dataframe_m11_2(dataframe)
    else:
        return "Wrong", "Wrong"

def validate_raw_fmu_76(dataframe: pd.DataFrame):
    unvalidated = []
    reasons = []
    return unvalidated, reasons

def validate_tables_fmu_76(dataframe: pd.DataFrame):
    unvalidated = []
    reasons = []
    return unvalidated, reasons


if __name__ == '__main__':
    df = pd.read_csv('src/report.csv', index_col=0)
    print(validate(df))
