import pandas as pd
import datetime

# Установим параметры подключения к БД
server = 'XXX'
port = 'XXX'
username = 'XXX'
password = 'XXX'
database = 'XXX'

# Определим структуру загружаемых данных и SQL-запрос
columns = [
    "Столбец_1",
    "Столбец_2",
    "Столбец_3",
]
def get_sql_text(last_session_time, new_session_time):
    columns_text = ", ".join(columns)
    return f""" 
        SELECT {columns_text}
        FROM ...
        WHERE '{last_session_time}' < time AND time <= '{new_session_time}'
    """

# Установим параметры подключения к Триафлай и "координаты" хранения времени последней загрузки данных
triafly_url = 'https://XXX.ru'
triafly_api_key = 'XXX'
triafly_set_id = 123            # id справочника "Сессии инкрементальной загрузки данных"
triafly_set_time_indicator_id = 123    # id показателя "Время последней сессии" в справочнике
triafly_set_element_id = 123         # id элемента (строки) справочника, соответствующего нужной сессии

# Определим время последней загрузки данных
from netdbclient import Connection
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
triafly_conn = Connection(triafly_url, triafly_api_key)
df = triafly_conn.get_block(block_or_descrs_list=[triafly_set_time_indicator_id], from_set=triafly_set_id)
last_session_time = df[df["id"]==triafly_set_element_id].iloc[0, 1]

# Определим время новой загрузки данных
new_session_time = datetime.datetime.now().isoformat()

print("Данные для загрузки") # Название таблицы
print(*columns, sep='\t') # Заголовки столбцов таблицы

# Произведем новую сессию загрузки данных
import pymssql
try:
    connection = pymssql.connect(
        server=server,
        user=username,
        password=password,
        database=database,
        port=port
    )
    cursor = connection.cursor()
    cursor.execute(get_sql_text(last_session_time, new_session_time))

    row = cursor.fetchone()
    while row:
        items = [item for item in row]
        print(*items, sep='\t')
        row = cursor.fetchone()

    # Запишем время новой сессии в справочник на платформе Триафлай
    triafly_conn.update_objects({triafly_set_element_id: {triafly_set_time_indicator_id: new_session_time}})
except:
    raise
finally:
    connection.close()