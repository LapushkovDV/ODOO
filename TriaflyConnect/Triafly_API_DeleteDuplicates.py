from netdbclient import Connection
import pandas as pd
from IPython.display import display
import ssl

import datetime

# Установим параметры подключения к Триафлай и "координаты" хранения времени последней загрузки данных
triaflyRegistr_FactwithFiltr = 1501179  # API Э_фактические показания приборов учета с фильтром для удаления дубликатов
pokazatelSerialPU = 472 #Э_Серийный номер ПУ
pokazatelDataPokaz = 474283 #Э_дата показаний

triaflyReportDataPokazKolvoAbonent = 1501104

def delete_duplicates(_strdate, triafly_conn_delete):
    # params = [
    #           {  'param_id': pokazatelSerialPU
    #             ,'param_val':[477]
    #             ,'param_index':0
    #           }
    #          ,{
    #               'param_id': pokazatelDataPokaz
    #             , 'param_val': [_strdate]
    #             , 'param_index': 0
    #
    #           }
    #          ]

    params = [{
                  'param_id': pokazatelDataPokaz
                , 'param_val': [_strdate]
                , 'param_index': 0
              }
             ]

    print(datetime.datetime.now(),'Ищем дубликаты за', _strdate)
    rspn_Registr_Fact = triafly_conn_delete.get_registry(triaflyRegistr_FactwithFiltr, params) ##params это реестр серийных номеров приборов учета
    #print(datetime.datetime.now(),"Получен реестр реестр серийных номеров приборов учета") # Название таблицы
    #display(rspn_Registr_Fact)
    duplicateRows = rspn_Registr_Fact[rspn_Registr_Fact.duplicated ()]
    #print(duplicateRows)
    #file_name = 'rspn_Registr_Fact.xlsx'

    # saving the excel
    #duplicateRows.to_excel(file_name)
    # print('DataFrame is written to Excel File successfully.')
    #
    #column_list_raw = list(duplicateRows.columns.values )
    #
    list_to_delete = []
    for index, row in duplicateRows.iterrows():
            list_to_delete.append(index)

    if list_to_delete:
        print(datetime.datetime.now(),'Удялем дубликаты за',_strdate )
        triafly_conn_delete.delete_objects(list_to_delete)

def check_all_dates():
    triafly_url = 'http://194.169.192.155:55556/'
    triafly_api_key = '8EBEA456a6'
    ssl._create_default_https_context = ssl._create_unverified_context
    triafly_conn = Connection(triafly_url, triafly_api_key)

    rspn_ReportDataPokazKolvoAbonent = triafly_conn.get(triaflyReportDataPokazKolvoAbonent)
    for row in rspn_ReportDataPokazKolvoAbonent:
        datepokaz = datetime.datetime.strptime(row[0], "%d.%m.%Y").date()
        #print(datepokaz)
        delete_duplicates(datepokaz.strftime("%Y-%m-%d"), triafly_conn)

# check_all_dates()