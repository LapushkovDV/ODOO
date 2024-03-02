from netdbclient import Connection
import pandas as pd
from IPython.display import display
import ssl

import datetime

# Установим параметры подключения к Триафлай и "координаты" хранения времени последней загрузки данных
triafly_url = 'http://194.169.192.155:55556/'
triafly_api_key = '8EBEA456a6'
ssl._create_default_https_context = ssl._create_unverified_context
triafly_conn = Connection(triafly_url, triafly_api_key)
triaflyRegistr_Fact = 497982 #этот реестр заполняем Э_фактические показания приборов учета
triaflyRegistrAbonent_PU = 864199 #API 5 Э_Приборы учета с абонентами и трансформаторами по периоду
pokazatelSerialPU = 472 #Э_Серийный номер ПУ
pokazatelDataPokaz = 474283 #Э_дата показаний

params = [
          {  'param_id': pokazatelSerialPU
            ,'param_val':[477]
            ,'param_index':0
          }
         ,{
              'param_id': pokazatelDataPokaz
            , 'param_val': ['2024-01-29']
            , 'param_index': 0

          }
         ]

params = [{
              'param_id': pokazatelDataPokaz
            , 'param_val': ['2024-01-29']
            , 'param_index': 0
          }
         ]


rspn_Registr_Fact = triafly_conn.get_registry(triaflyRegistr_Fact, params) ##params это реестр серийных номеров приборов учета
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
    print('Удялем дубликаты')
    triafly_conn.delete_objects(list_to_delete)