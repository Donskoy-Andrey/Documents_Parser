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
    :return: True if the candidate can be floated
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


def validate_raw_data_m11(dataframe: pd.DataFrame) -> Tuple[list, list[str]]:
    """
    Validation of values in the FMU-76 document
    :param dataframe: column: "Значение" values in the FMU-76 document
    :return:
        list of indexes with wrong col, list of reasons
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
    """
    identify a type of dataframe on document M-11
    :param dataframe: parsed from document M-11
    :return:
    """
    if dataframe.columns[0] in ["Дата составления", "Дата\nсоставления"]:
        return 1
    elif dataframe.columns[0] in ["Корреспондирующий счет", "Корреспондирующий\nсчет"]:
        return 2
    return 3


def check_date(date: str) -> bool:
    """
    check if date in format dd.mm.yyyy
    :param date: string
    :return: true if date is valid, false otherwise
    """
    try:
        day, month, year = date.split(".")
    except ValueError:
        return False
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


def validate_dataframe_m11_1(dataframe: pd.DataFrame) -> Tuple[list, list]:
    """
    validate table from document M-11 (type 1)
    use function identify_df to get type
    :param dataframe: parsed from a document
    :return:
     two lists: a first list is "coordinates" unvalidated cell (index, column),
     a second list is reasons why unvalidated
    """
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
            reasons.append("Нет данных о отправителе")
        if not receiver_info:
            cols = [col for col in dataframe.columns if "Получатель" in col]
            for col in cols:
                unvalidated.append((index, col))
            reasons.append("Нет данных о получателе")

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
    """
    validate table from document M-11 (type 2)
    (use function ```identify_df``` to get type)
    :param dataframe: parsed from a document
    :return:
     two lists: a first list is "coordinates" unvalidated cell (index, column),
     a second list is reasons why unvalidated
    """
    reasons = []
    unvalidated = []
    for index, row in dataframe.iterrows():
        if index == 2:
            continue
        corresponding_account = [col for col in dataframe.columns if "Корреспондирующий счет" in col]
        for col in corresponding_account:
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
                    unvalidated.append((index, col))
                    reasons.append(f"{col}: Неправильный денежный формат (руб,коп)")
                else:
                    rub, kop = row[col].split(",")
                    rub = rub.replace(" ", "").replace("\n", "")
                    kop = kop.replace(" ", "").replace("\n", "")
                    if not rub.isdigit() or not kop.isdigit():
                        unvalidated.append((index, col))
                        reasons.append(f"{col}: Неправильный денежный формат (руб,коп)")

            except AttributeError:
                unvalidated.append((index, col))
                reasons.append(f"{col}: Неправильный денежный формат (руб,коп)")
    return unvalidated, reasons


def validate_tables_m11(dataframe: pd.DataFrame):
    """
    validate tables from M-11
    :param dataframe: parsed from M-11
    :return:
    if correct data, return tuple with 2 lists:
        a first list is "coordinates" unvalidated cell (index, column),
        a second list is reasons why unvalidated
    if incorrect data, return ("Wrong", "Wrong")
    """
    df_type = identify_df(dataframe)
    if df_type == 1:
        return validate_dataframe_m11_1(dataframe)
    elif df_type == 2:
        return validate_dataframe_m11_2(dataframe)
    else:
        return "Wrong", "Wrong"


def check_type_from(value: str) -> bool:
    if "Специализированная форма № ФМУ-76" in value:
        return True
    else:
        return False


def check_structure_department(value: str) -> bool:
    if "Север" in value and "Кавказ" in value:
        return True
    else:
        return False


def check_post(value: str) -> bool:
    """
    Validation of the position by whom the document FMU-76 was approved.
    The document cannot be validated by anyone other than the supervisor.
    :param value: position
    :return:
        True if the supervisor
    """
    if "Начальник" in value:
        return True
    else:
        return False


def check_name(value: str) -> bool:
    """
    Validation of correctness of filling
    in the full name in the FMU-76 document

    :param value: full name
    :return:
        True if everything is correct.
    """
    names = value.split(' ')
    for i in names:
        if len(i) <= 1 or i[0] == i[0].lower():
            return False
    return True


def validate_raw_fmu_76(dataframe: pd.DataFrame) -> tuple[list, list]:

    unvalidated = []
    reasons = []
    col_name = "Значение"
    for index, row in dataframe.iterrows():
        value = row[col_name]
        if index == "Тип формы":
            if not check_type_from(value):
                unvalidated.append(index)
                reasons.append("Неверное тип формы")
        elif index == "Номер акта":
            if not value.isdigit():
                unvalidated.append(index)
                reasons.append("Номер акта не является числом")
                continue
            try:
                int(value)
            except ValueError:
                unvalidated.append(index)
                reasons.append("Номер акта не является  натуральным числом")
        elif index == "Дата акта":
            if not check_date(value):
                unvalidated.append(index)
                reasons.append("Неверная дата акта")
        elif index == "Организация":
            if not check_organization(value):
                unvalidated.append(index)
                reasons.append("Неверное название организации")
        elif index == "Структурное подразделение":
            if not check_structure_department(value):
                unvalidated.append(index)
                reasons.append("Структурное подразделение не является Северо- Кавказским")
        elif index == "Утверждено (должность)":
            if not check_post(value):
                unvalidated.append(index)
                reasons.append("Утверждено не начальником")
        elif index == "Утверждено (ФИО)":
            if not check_name(value):
                unvalidated.append(index)
                reasons.append("Некорректно заполнено ФИО")
        elif index == "Утверждено (дата)":
            if not check_date(value):
                unvalidated.append(index)
                reasons.append("Неверная дата утверждения")
        elif "Коды" in index:
            if not check_float(value):
                unvalidated.append(index)
                reasons.append(f"{index}: Неверный формат номера (только числа)")

    return unvalidated, reasons


def identify_df_fmu(dataframe: pd.DataFrame) -> Literal[1, 2, 3]:
    """
    identify a type of dataframe on document ФМУ-76
    :param dataframe: parsed from document ФМУ-76
    :return:
    """
    if dataframe.columns[0] in ["Структурное подразделение (цех, участок и др.)"]:
        return 1
    elif dataframe.columns[0] in ['Технический счет 32 "Затраты"', ]:
        return 2
    return 3


def validate_dataframe_fmu_1(df: pd.DataFrame):
    """
    validate table from document ФМУ-76(type 1)
    (use function ```identify_df``` to get type)
    :param df: parsed from a document
    :return:
     two lists: a first list is "coordinates" unvalidated cell (index, column),
     a second list is reasons why unvalidated
    """
    reasons = []
    unvalidated = []
    for index, row in df.iterrows():
        if len(row["Структурное подразделение (цех, участок и др.)"]) < 3:
            unvalidated.append((index, "Структурное подразделение (цех, участок и др.)"))
            reasons.append(f"Структурное подразделение (цех, участок и др.): Неправильное название организации")
        if not row["Код операции"].isdigit():
            unvalidated.append((index, "Код операции"))
            reasons.append(f"Код операции: Допустимы только цифры!")
        if row["Корреспондирующий счет (Cчет, субчет)"].isdigit():
            pass
        else:
            unvalidated.append((index, "Корреспондирующий счет (Cчет, субчет)"))
            reasons.append(f"Корреспондирующий счет (Cчет, субчет): Некорректно задан")
        if row["Корреспондирующий счет (Статья расходов/носитель затрат)"].isdigit():
            pass
        else:
            unvalidated.append((index, "Корреспондирующий счет (Статья расходов/носитель затрат)"))
            reasons.append(f"Корреспондирующий счет (Статья расходов/носитель затрат): Допустимы только цифры!")
    return unvalidated, reasons




def validate_dataframe_fmu_2(df: pd.DataFrame):
    """
    validate table from document ФМУ-76(type 2)
    (use function ```identify_df``` to get type)
    :param df: parsed from a document
    :return:
     two lists: a first list is "coordinates" unvalidated cell (index, column),
     a second list is reasons why unvalidated
    """
    reasons = []
    unvalidated = []
    numeric_fields = [
        'Технический счет 32 "Затраты"',
        'Корреспондирующий счет (Cчет, субчет)',
        'Материальные ценности (номенклатурный номер)',
        'Единица измерения (код)',
    ]
    float_fields = [
        'Нормативное количество',
        'Фактически израсходованно (Количество)',
        'Отклонение фактического расхода от нормы ("-" экономия,"+" перерасход)'
    ]
    money_fields = [
        'Фактически израсходованно (Цена, руб.коп)',
        'Фактически израсходованно (Сумма, руб.коп)',
    ]
    for index, row in df.iterrows():
        if index == 2:
            continue

        for col in numeric_fields:
            if row[col].isnumeric():
                pass
            else:
                unvalidated.append((index, col))
                reasons.append(f'{col}: Допустимы только цифры!')

        for col in float_fields:
            if check_float(row[col]) and len(row[col].split('.')[-1]) == 3:
                pass
            else:
                unvalidated.append((index, col))
                reasons.append(f'{col}: Пример формата: 1.000')
        for col in money_fields:
            if check_float(row[col]):
                pass
            else:
                unvalidated.append((index, col))
                reasons.append(f'{col}: Не число!')

        if row['Производстенный заказ'].isalnum():
            pass
        else:
            col = 'Производстенный заказ'
            unvalidated.append((index, col))
            reasons.append(f'{col}: Допустимы только цифры!')
    return [], []


def validate_tables_fmu_76(dataframe: pd.DataFrame):
    """
    validate tables from ФМУ-76
    :param dataframe: parsed from ФМУ-76
    :return:
    if correct data, return tuple with 2 lists:
        a first list is "coordinates" unvalidated cell (index, column),
        a second list is reasons why unvalidated
    if incorrect data, return ("Wrong", "Wrong")
    """

    df_type = identify_df_fmu(dataframe)
    # print(f"{df_type=}")
    if df_type == 1:
        return validate_dataframe_fmu_1(dataframe)
    elif df_type == 2:
        return validate_dataframe_fmu_2(dataframe)
    else:
        return "Wrong", "Wrong"



if __name__ == '__main__':
    df = pd.read_csv('src/report.csv', index_col=0)
    # print(validate(df))
