import camelot
import pandas as pd
import logging
import os

logging.basicConfig(level=logging.INFO)

columns_table1_m11 = ['Дата составления','Код вида операции','Отправитель (структурное подразделение)',
         'Отправитель (табельный номер МОЛ (ЛОС))','Получатель (структурное подразделение)','Получатель (табельный номер МОЛ (ЛОС))',
         'Корреспондирующий счет (cчет, cубсчет)', 'Корреспондирующий счет (код аналитического учета)', 'Учетная единица выпуска продукции (работ,услуг)']

columns_table2_m11 = ['Корреспондирующий счет', 'Материальные ценности (наименование)', 'Материальные ценности (номенклатурный номер)',
        'Характеристика','Заводской номер', 'Инвентарный номер', 'Сетевой номер',
        'Единица измерения (код)', 'Единица измерения (наименование)', 'Количество (затребовано)', 'Количество (отпущено)',
        'Цена руб.коп', 'Сумма без учета НДС,руб.коп.', 'Порядковый номер по складской картотеке',
        'Местонахождение', 'Регистрационный номер партии товара, подлежащего прослеживаемости']

columns_table1_fmu76 = ['Структурное подразделение (цех, участок и др.)','Код операции',
                      'Корреспондирующий счет (Cчет, субчет)','Корреспондирующий счет (Статья расходов/носитель затрат)']

columns_table2_fmu76 = ['Технический счет 32 "Затраты"', 'Производстенный заказ',
                      'Корреспондирующий счет (Cчет, субчет)', 'Корреспондирующий счет (код аналитического учета)',
                      'Материальные ценности (наименование, сорт, размер, марка)', 'Материальные ценности (номенклатурный номер)',
                      'Заводской номер детали','Единица измерения (код)', 'Единица измерения (наименование)', 'Нормативное количество',
                      'Фактически израсходованно (Количество)', 'Фактически израсходованно (Цена, руб.коп)', 'Фактически израсходованно (Сумма, руб.коп)',
                      'Отклонение фактического расхода от нормы ("-" экономия,"+" перерасход)', 'Вид работ или ремонта, содержание хозяйственной операции',
                      'Срок полезного использования использования, причина отклонения в расходе и другое',
                      'Регистрационный номерпартии товара,подлежащего прослеживаемости']


def table_ocr_m11(path: str | None) -> list[pd.DataFrame,pd.DataFrame]:
    """
    Obtaining and correcting tables in the M-11 file
    :param path: file path
    :return:
        list from a table in DataFrame format
    """
    if path is None:
        logging.critical('Неверный путь')
        return []
    if os.path.split(path)[1].split('.')[-1] != 'pdf':
        logging.critical('Неверный тип файла')
        return []

    tables = camelot.read_pdf(path,pages='all',)
    tables = tables[1:-1]
    tables = [tabl.df for tabl in tables]

    index = 1
    while index < len(tables):
        if tables[index-1].shape[1] == tables[index].shape[1]:
            tab = tables[index].iloc[3:]
            if len(tab.iloc[0, 0]) == 0:
                line2 = tab.iloc[0,:]
                for i, val in enumerate(line2):
                    tables[index - 1].iloc[-1,i] += str(val)
                tables[index - 1] = pd.concat([tables[index - 1], tables[index].iloc[4:]])
            else:
                tables[index - 1] = pd.concat([tables[index-1],tables[index].iloc[3:]])
            del tables[index]
        else:
            index += 1

    tables[0].columns = columns_table1_m11
    tables[0].drop([0, 1], axis=0, inplace=True)
    tables[1].columns = columns_table2_m11
    tables[1].drop([0, 1, 2], axis=0, inplace=True)
    return clear_dataframe(tables[:2])


def table_ocr_fmu76(path: str | None) -> list[pd.DataFrame,pd.DataFrame]:
    """
    Obtaining and correcting tables in the FMU-76 file
    :param path: file path
    :return:
        list from a table in DataFrame format
    """
    tables = camelot.read_pdf(path, pages='all')
    tables = tables[:-1]
    tables = [tabl.df for tabl in tables]

    index = 1
    while index < len(tables):
        if tables[index-1].shape[1] == tables[index].shape[1]:
            tab = tables[index].iloc[3:]
            if len(tab.iloc[0, 0]) == 0:
                line2 = tab.iloc[0,:]
                for i, val in enumerate(line2):
                    tables[index - 1].iloc[-1,i] += str(val)
                tables[index - 1] = pd.concat([tables[index - 1], tables[index].iloc[4:]])
            else:
                tables[index - 1] = pd.concat([tables[index-1],tables[index].iloc[3:]])
            del tables[index]
        else:
            index += 1

    if len(tables) > 1:
        table1_fmu_2_2 = tables[0].iloc[2, 2].split('\n')
        tables[0].iloc[2, 2] = table1_fmu_2_2[0]
        tables[0].drop([0, 1], axis=0, inplace=True)
        tables[0].columns = columns_table1_fmu76[:-1]
        tables[0][columns_table1_fmu76[-1]] = table1_fmu_2_2[-1]

        tables[1].columns = columns_table2_fmu76
        tables[1].drop([0, 1, 2], axis=0, inplace=True)
    else:
        # Can't see first table
        tables[0].columns = columns_table2_fmu76
        tables[0].drop([0, 1, 2], axis=0, inplace=True)

    return clear_dataframe(tables[:2])


def clear_dataframe(tables: list[pd.DataFrame,pd.DataFrame]) -> list[pd.DataFrame,pd.DataFrame]:
    """
    Clear DataFrame
    :param tables:  list from a table in DataFrame
    :return:
        list from a table in DataFrame
    """
    tables = [
        table.replace('\n', '', regex=True)
        for table in tables
    ]
    return tables


if __name__ == '__main__':
    pass
