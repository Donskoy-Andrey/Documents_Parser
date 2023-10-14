import camelot
import pandas as pd
import logging
import os

logging.basicConfig(level=logging.INFO)


def table_ocr(path: str | None) -> list[pd.DataFrame]:
    if path is None:
        logging.critical('Неверный путь')
        return []
    if os.path.split(path)[1].split('.')[-1] != 'pdf':
        logging.critical('Неверный тип файла')
        return []

    tables = camelot.read_pdf(path,pages='all',)
    tables = [tabl.df for tabl in tables]
    len_colunms_tabl = []
    for tabl in tables:
        tabl.columns = tabl.loc[0,:].values
        tabl.drop(0, axis=0, inplace=True)
        len_colunms_tabl.append(tabl.shape[1])

    index = 1
    while index < len(tables):
        if tables[index-1].shape[1] == tables[index].shape[1]:
            tables[index - 1] = pd.concat([tables[index-1],tables[index].iloc[2:]])
            del tables[index]
        else:
            index += 1
    tables = tables[:-1]
    return tables


if __name__ == '__main__':
    # dfs = cut_table_from_pdf("data/test1.pdf")
    # print(dfs[0].to_excel("data/ali1.xlsx"))
    # print(dfs[1].to_excel("data/ali2.xlsx"))
    # print(dfs[2].to_excel("data/ali3.xlsx"))
    pass
