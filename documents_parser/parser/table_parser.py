import camelot
import pandas as pd
import logging
import os

logging.basicConfig(level=logging.INFO)

columns_table1 = ['Дата составления','Код вида операции','Отправитель(структурное подразделение)',
         'Отправитель(табельный номер МОЛ (ЛОС))','Получатель(структурное подразделение)','Получатель (табельный номер МОЛ (ЛОС))',
         'Корреспондирующий счет(cчет, cубсчет)', 'Корреспондирующий счет(код аналитического учета)', 'Учетная единица выпуска продукции(работ,услуг)']

columns_table2 = ['Корреспондирующий счет', 'Материальные ценности(наименование)', 'Материальные ценности(коменклатурный номер)',
        'Характеристика','Заводской номер', 'Инвентарный номер', 'Сетевой номер',
        'Единица измерения(код)', 'Единица измерения(наименование)', 'Количество(затребовано)', 'Количество(отпущено)',
        'Цена руб.коп','Сумма без учета НДС,руб.коп.','Порядковй номер по складской картотеке',
        'Местонахождение','Регистрационный номер партии товара, подлежащего прослеживаемости']

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
    # tables = tables[1:-1]


    tables[0].columns = columns_table1
    tables[0].drop([0,1], axis=0, inplace=True)
    tables[1].columns = columns_table2
    tables[1].drop([0,1], axis=0, inplace=True)
    return tables[:2]


if __name__ == '__main__':
    # dfs = table_ocr("data/М-11/Принято/М11_123_23.06.2023.pdf")
    # print(dfs[0].to_excel("data/ali1.xlsx"))
    # print(dfs[1].to_excel("data/ali2.xlsx"))
    # print(dfs[2].to_excel("data/ali3.xlsx"))
    pass
