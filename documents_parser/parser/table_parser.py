import camelot
import pandas as pd
import logging
import os

logging.basicConfig(level=logging.INFO)

columns_table1 = ['Дата\nсоставления','Код вида\nоперации','Отправитель\n(структурное подразделение)',
         'Отправитель\n(табельный номер МОЛ (ЛОС)','Получатель\n(структурное подразделение)','Получатель\n(табельный номер МОЛ (ЛОС)',
         'Корреспондирующий счет\n(cчет, cубсчет)', 'Корреспондирующий счет\n(код аналитического учета)', 'Учетная единица\nвыпуска продукции\n(работ,услуг)']

columns_table2 = ['Корреспондирующий\nсчет', 'Материальные ценности\n(наименование)', 'Материальные ценности\n(коменклатурный номер)',
        'Характеристика','Заводской\nномер', 'Инвентарный\nномер', 'Сетевой\nномер',
        'Единица\nизмерения\n(код)', 'Единица\nизмерения\n(наименование)', 'Количество\n(затребовано)', 'Количество\n(отпущено)',
        'Цена\nруб.коп','Сумма без учета НДС,\nруб.коп.','Порядковй номер по\nскладской картотеке',
        'Местонахождение','Регистрационный\nномер партии товара,\nподлежащего\nпрослеживаемости']


def table_ocr(path: str | None) -> list[pd.DataFrame]:
    if path is None:
        logging.critical('Неверный путь')
        return []
    if os.path.split(path)[1].split('.')[-1] != 'pdf':
        logging.critical('Неверный тип файла')
        return []

    tables = camelot.read_pdf(path,pages='all',)
    tables = tables[1:-1]
    tables = [tabl.df for tabl in tables]
    # for tabl in tables:
    #     print(tabl.head())
    #     # tabl.columns =  tabl.loc[0,:].values
    #     # tabl.drop(0, axis=0, inplace=True)

    index = 1
    while index < len(tables):
        if tables[index-1].shape[1] == tables[index].shape[1]:
            tables[index - 1] = pd.concat([tables[index-1],tables[index].iloc[2:]])
            del tables[index]
        else:
            index += 1

    tables[0].columns = columns_table1
    tables[0].drop([0, 1], axis=0, inplace=True)
    tables[1].columns = columns_table2
    tables[1].drop([0, 1], axis=0, inplace=True)
    return tables[:2]


if __name__ == '__main__':
    # dfs = table_ocr("data/М-11/Принято/М11_123_23.06.2023.pdf")
    # print(dfs[0].to_excel("data/ali1.xlsx"))
    # print(dfs[1].to_excel("data/ali2.xlsx"))
    # print(dfs[2].to_excel("data/ali3.xlsx"))
    pass
