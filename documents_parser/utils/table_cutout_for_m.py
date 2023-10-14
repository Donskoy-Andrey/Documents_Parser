import camelot
import pandas as pd
import logging
import os
logging.basicConfig(level=logging.INFO)


def cut_table_from_pdf(path:str|None) -> list[pd.DataFrame]:
    if path is None:
        logging.critical('неверный путь')
        return
    if os.path.split(path)[1].split('.')[-1] != 'pdf':
        logging.critical('Неверный тип файла')
        return
    tables = camelot.read_pdf(path,pages='all',)
    tables = [tabl.df for tabl in tables]
    len_colunms_tabl = []
    for tabl in tables:
        tabl.columns = tabl.loc[0,:].values
        tabl.drop(0, axis=0, inplace=True)
        len_colunms_tabl.append(tabl.shape[1])

    index = 1
    while index  < len(tables):
        if tables[index-1].shape[1] == tables[index].shape[1]:
            tables[index -1 ] = pd.concat([tables[index-1],tables[index].iloc[2:]])#.iloc[2:]
            del tables[index]
        else:
            index += 1
    tables = tables[:-1]
    return tables


if __name__ == '__main__':
    cut_table_from_pdf("data/М-11/Принято/М11_123_23.06.2023.pdf")