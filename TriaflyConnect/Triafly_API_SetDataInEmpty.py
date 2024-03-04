from netdbclient import Connection
import pandas as pd
from IPython.display import display
import ssl

import datetime

# Установим параметры подключения к Триафлай и "координаты" хранения времени последней загрузки данных
triaflyRegistr_FactwithFiltr = 1501179  # API Э_фактические показания приборов учета с фильтром для удаления дубликатов
pokazatelSerialPU = 472 #Э_Серийный номер ПУ
pokazatelDataPokaz = 474283 #Э_дата показаний
pokazatelTransformator = 462056 #Э_Трансформатор

pokazatelTransformatorEmpty = 1857859 # трансформатор "--не привязанные ПУ--"

triaflyReportDataPokazKolvoAbonent = 1501104

triafly_url = 'http://194.169.192.155:55556/'
triafly_api_key = '8EBEA456a6'
ssl._create_default_https_context = ssl._create_unverified_context
triafly_conn_dataEmpty = Connection(triafly_url, triafly_api_key)
_strdate = '2024-02-18'
params = [
          {  'param_id': pokazatelTransformator
            ,'param_val':[1857859]
            ,'param_index':0
          }
         ,{
              'param_id': pokazatelDataPokaz
            , 'param_val': [_strdate]
            , 'param_index': 0

          }
         ]

print(datetime.datetime.now(),'Ищем пустые', _strdate)
rspn_Registr_Fact = triafly_conn_dataEmpty.get_registry(triaflyRegistr_FactwithFiltr, params) ##params это реестр серийных номеров приборов учета
print(rspn_Registr_Fact) # Название таблицы
#display(rspn_Registr_Fact)
