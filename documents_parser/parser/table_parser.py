import camelot
import pandas as pd
import logging
import os

logging.basicConfig(level=logging.INFO)

columns_table1_m = ['Дата составления','Код вида операции','Отправитель(структурное подразделение)',
         'Отправитель(табельный номер МОЛ (ЛОС))','Получатель(структурное подразделение)','Получатель (табельный номер МОЛ (ЛОС))',
         'Корреспондирующий счет(cчет, cубсчет)', 'Корреспондирующий счет(код аналитического учета)', 'Учетная единица выпуска продукции(работ,услуг)']

columns_table2_m = ['Корреспондирующий счет', 'Материальные ценности(наименование)', 'Материальные ценности(номенклатурный номер)',
        'Характеристика','Заводской номер', 'Инвентарный номер', 'Сетевой номер',
        'Единица измерения(код)', 'Единица измерения(наименование)', 'Количество(затребовано)', 'Количество(отпущено)',
        'Цена руб.коп','Сумма без учета НДС,руб.коп.','Порядковй номер по складской картотеке',
        'Местонахождение','Регистрационный номер партии товара, подлежащего прослеживаемости']

columns_table1_fmy = ['Структурное подразделение(цех, участок и др.)','Код операции',
                      'Корреспондирующий счет(Cчет, субчет)','Корреспондирующий счет(Статья расходов/носитель затрат)']

columns_table2_fmy = ['Технический счет 32 "Затраты"','Производстенный заказ',
                      'Корреспондирующий счет(Cчет, субчет)','Корреспондирующий счет(код аналитического учета)',
                      'Материальные ценности(наименование, сорт, размер, марка)','Материальные ценности(номенклатурный номер)',
                      'Заводской номер детали','Единица измерения(код)', 'Единица измерения(наименование)','Нормативное количество',
                      'Фактически израсходованно(Количество)','Фактически израсходованно(Цена, руб.коп)','Фактически израсходованно(Сумма, руб.коп)',
                      'Отклонение фактического расхода от нормы ("-" экономия,"+" перерасход)','Вид работ или ремонта, содержание хозяйственной операции',
                      'Срок полезного использования использования, причина отклонения в расходе и другое',
                      'Регистрационный номерпартии товара,подлежащего прослеживаемости']




def table_ocr_m(path: str | None) -> list[pd.DataFrame]:
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

    tables[0].columns = columns_table1_m
    tables[0].drop([0,1], axis=0, inplace=True)
    tables[1].columns = columns_table2_m
    tables[1].drop([0,1], axis=0, inplace=True)
    return cler_DataFrame(tables[:2])

def  table_ocr_fmy(path: str | None) -> list[pd.DataFrame]:
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

    table1_fmy_2_2 = tables[0].iloc[2,2].split('\n')
    tables[0].iloc[2, 2] = table1_fmy_2_2[0]
    tables[0].drop([0,1],axis=0, inplace=True)
    tables[0].columns = columns_table1_fmy[:-1]
    tables[0][columns_table1_fmy[-1]] = table1_fmy_2_2[-1]

    tables[1].columns = columns_table2_fmy
    tables[1].drop([0,1], axis=0, inplace=True)
    # print(tables[1].to_excel("data/ali2.xlsx"))
    return cler_DataFrame(tables[:2])

def cler_DataFrame(tables:list[pd.DataFrame]) -> list[pd.DataFrame]:
    tables = [tabl.replace('\n', '', regex=True) for tabl in tables]
    # print(tables[1].to_excel("data/ali2.xlsx"))
    # print(tables[1])
    return tables





if __name__ == '__main__':
    # dfs = table_ocr("data/М-11/Принято/М11_123_23.06.2023.pdf")
    # print(dfs[0].to_excel("data/ali1.xlsx"))
    # print(dfs[1].to_excel("data/ali2.xlsx"))
    # print(dfs[2].to_excel("data/ali3.xlsx"))
    # table_ocr_fmy("data/ФМУ-76/Аннулировано/фму-76_3478_17.07.2023.pdf")


    pass
