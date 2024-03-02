from netdbclient import Connection
import pandas as pd
from IPython.display import display
import ssl

import datetime


# Установим параметры подключения к Триафлай и "координаты" хранения времени последней загрузки данных
triafly_url = 'http://194.169.192.155:55556/'
triafly_api_key = '8EBEA456a6'
triafly_set_id = 123            # id справочника "Сессии инкрементальной загрузки данных"
triafly_set_time_indicator_id = 123    # id показателя "Время последней сессии" в справочнике
triafly_set_element_id = 123         # id элемента (строки) справочника, соответствующего нужной сессии

# Определим время последней загрузки данных


def get_id_catalog_by_value(catalog, value):
    for one_elem in catalog:
        #print("'",one_Abon_PU[0],"'",type(one_Abon_PU[0]),"'", serial,"'", type(serial))#
        if str(one_elem[0]) == str(value):
            #print('EQUAL')
            return one_elem[1]
    return ''

def get_info_elem_from_registry( _registry, serial, npp, strdate):
    for one_elem in _registry:
        #print("'",one_Abon_PU[0],"'",type(one_Abon_PU[0]),"'", serial,"'", type(serial))#
        # print('strdate = ', strdate)
        # print('one_Abon_PU[0] =', one_Abon_PU[0])
        # print('one_Abon_PU[1] =', one_Abon_PU[1])
        curDate = datetime.datetime.strptime(strdate, "%d.%m.%Y").date()
        begDate = datetime.datetime.strptime(one_elem[0], "%d.%m.%Y").date()
        endDate = datetime.datetime.strptime(one_elem[1], "%d.%m.%Y").date()

        if ( (str(one_elem[npp]) == str(serial)) and (curDate >= begDate) and (curDate <= endDate)):
            #print('EQUAL')
            return one_elem

def get_info_elem_from_registry( _registry, serial, npp, strdate):
    for one_elem in _registry:
        #print("'",one_Abon_PU[0],"'",type(one_Abon_PU[0]),"'", serial,"'", type(serial))#
        # print('strdate = ', strdate)
        # print('one_Abon_PU[0] =', one_Abon_PU[0])
        # print('one_Abon_PU[1] =', one_Abon_PU[1])
        curDate = datetime.datetime.strptime(strdate, "%d.%m.%Y").date()
        begDate = datetime.datetime.strptime(one_elem[0], "%d.%m.%Y").date()
        endDate = datetime.datetime.strptime(one_elem[1], "%d.%m.%Y").date()

        if ( (str(one_elem[npp]) == str(serial)) and (curDate >= begDate) and (curDate <= endDate)):
            #print('EQUAL')
            return one_elem

ssl._create_default_https_context = ssl._create_unverified_context
triafly_conn = Connection(triafly_url, triafly_api_key)


triaflyRegistr_PU = 1320709 #это реестр серийных номеров приборов учета
triaflyRegistr_Fact = 497982 #этот реестр заполняем Э_фактические показания приборов учета
triaflyRegistr_Abon_PU = 864199 # реестр Э_Реестр: абонент + прибор учёта (ПУ). /0 серийный номер ПУ/1 Абонент/2 Э_с (дата)/ Э_по (дата)/4 трансформатор
triaflyRegistr_LineAbonent = 472220 # реестр Э_Реестр: линия + абонент
triaflyRegistr_TransfLine = 472890 # реестр Э_Трансформатор+линия+мощность рубильника линии
triaflyRegistr_TPTransf = 473239 # реестр Э_ТП+трансформатор+мощность рубильника трансформатора

triaflyReportPoluchasyID = 498110 # отчет Э_Получасы ID
triaflyReportAbonentID = 498223   # отчет Э_Абоненты ID
triaflyReportSerPU_ID = 498250    # отчет Э_Серийный номер ПУ ID
triaflyReportLine_ID = 598213     # отчет Э_Линия ID
triaflyReportTransf_ID = 598279   # отчет Э_Трансформатор ID
triaflyReportTP_ID = 598236       # отчет Э_ТП(Трансформаторная подстанция) ID
triaflyReportNasPunkt_ID = 598302 # отчет Э_Населенный пункт ID
triaflyReportLineAV = 876586      # API Э_АВ линии (автоматический выключатель/рубильник) ID
triaflyReportTransfAV = 876613    # API Э_АВ трансформатора (автоматический выключатель/рубильник) ID

print(datetime.datetime.now(),"Данные для загрузки") # Название таблицы


rspn_registry_PU = triafly_conn.get(triaflyRegistr_PU) ##это реестр серийных номеров приборов учета
print(datetime.datetime.now(),"Получен реестр реестр серийных номеров приборов учета") # Название таблицы

rspn_registry_Abon_PU = triafly_conn.get(triaflyRegistr_Abon_PU) # реестр пересечения абонентов и приборов учета по времени
print(datetime.datetime.now(),"Получен реестр пересечения абонентов и приборов учета по времени") # Название таблицы

rspn_registry_LineAbonent = triafly_conn.get(triaflyRegistr_LineAbonent) # реестр Э_Реестр: линия + абонент
print(datetime.datetime.now(),"Получен реестр Э_Реестр: линия + абонент + мощность")
rspn_registry_TransfLine = triafly_conn.get(triaflyRegistr_TransfLine) # реестр Э_Трансформатор+линия+мощность рубильника линии
print(datetime.datetime.now(),"Получен реестр Э_Трансформатор+линия+мощность рубильника линии")
rspn_registry_TPTransf = triafly_conn.get(triaflyRegistr_TPTransf) # реестр Э_ТП+трансформатор+мощность рубильника трансформатора
print(datetime.datetime.now(),"Получен реестр Э_ТП+трансформатор+мощность рубильника трансформатора")
rspPoluchasyID = triafly_conn.get(triaflyReportPoluchasyID) # тут список получасов с их ID
print(datetime.datetime.now(),"Получен отчет список получасов с их ID")
rspAbonentID  = triafly_conn.get(triaflyReportAbonentID) # список абонентов с ID
print(datetime.datetime.now(),"Получен отчет список абонентов с ID")
rspSerPU_ID  = triafly_conn.get(triaflyReportSerPU_ID) # список сериных номепроов ПУ
print(datetime.datetime.now(),"Получен отчет список сериных номепроов ПУ с ID ")
rspLine_ID = triafly_conn.get(triaflyReportLine_ID)      # отчет Э_Линия ID
print(datetime.datetime.now(),"Получен отчет список Э_Линия ID")
rspTransf_ID = triafly_conn.get(triaflyReportTransf_ID)    # отчет Э_Трансформатор ID
print(datetime.datetime.now(),"Получен отчет список Э_Трансформатор c ID")
rspTP_ID = triafly_conn.get(triaflyReportTP_ID)        # отчет Э_ТП(Трансформаторная подстанция) ID
print(datetime.datetime.now(),"Получен отчет список Э_ТП(Трансформаторная подстанция) c ID")
rspNasPunkt_ID = triafly_conn.get(triaflyReportNasPunkt_ID)  # отчет Э_Населенный пункт ID
print(datetime.datetime.now(),"Получен отчет список Э_Населенный пункт c ID")
rspLineAV_ID = triafly_conn.get(triaflyReportLineAV)     # API Э_АВ линии (автоматический выключатель/рубильник) ID
print(datetime.datetime.now(),"Получен отчет API Э_АВ линии (автоматический выключатель/рубильник) ID")
rspTransfAV_ID = triafly_conn.get(triaflyReportTransfAV) # API Э_АВ трансформатора (автоматический выключатель/рубильник) ID
print(datetime.datetime.now(),"Получен отчет API Э_АВ трансформатора (автоматический выключатель/рубильник) ID")
excel_file_df=''
#display(rspSerPU_ID)

#triafly_conn.put([['29.01.2024', '593' ,999]],498058)

#excel_file_df = pd.read_excel(r'C:\Users\Дмитрий\YandexDisk\Work\Систематика\Энсис АСКУЭ\06_2_ТУ_на_ПС_с_показаниями,_30_минут_24_11216.xlsx', skiprows=range(4), dtype='object')
#excel_file_df = pd.read_excel(r'C:\Users\Дмитрий\YandexDisk\Work\Систематика\Энсис АСКУЭ\06_2_ТУ_на_ПС_с_показаниями,_30_минут_24_11082.xlsx', skiprows=range(4), dtype='object')
#excel_file_df = pd.read_excel(r'C:\Users\Дмитрий\YandexDisk\Work\Систематика\Энсис АСКУЭ\20240227\TEst.xlsx', skiprows=range(4), dtype='object')

#excel_file_df = pd.read_excel(r'C:\Users\Дмитрий\YandexDisk\Work\Систематика\Энсис АСКУЭ\20240227\06_2_ТУ_на_ПС_с_показаниями,_30_минут_24.xlsx', skiprows=range(4), dtype='object')
#excel_file_df = pd.read_excel(r'C:\Users\Дмитрий\YandexDisk\Work\Систематика\Энсис АСКУЭ\20240227\06_2_ТУ_на_ПС_с_показаниями,_30_минут_25 (2).xlsx', skiprows=range(4), dtype='object')
#excel_file_df = pd.read_excel(r'C:\Users\Дмитрий\YandexDisk\Work\Систематика\Энсис АСКУЭ\20240227\06_2_ТУ_на_ПС_с_показаниями,_30_минут_25.xlsx', skiprows=range(4), dtype='object')
#excel_file_df = pd.read_excel(r'C:\Users\Дмитрий\YandexDisk\Work\Систематика\Энсис АСКУЭ\20240227\06_2_ТУ_на_ПС_с_показаниями,_30_минут_26.xlsx', skiprows=range(4), dtype='object')

print(datetime.datetime.now(),"Прочитан EXCEL-файл")
#excel_file_df = pd.read_excel(r'C:\Users\Дмитрий\YandexDisk\Work\Систематика\Энсис АСКУЭ\test_transf.xlsx', skiprows=range(4), dtype='object')

#display(excel_file_df)

excel_file_df = excel_file_df.reset_index()
column_list_raw = list(excel_file_df.columns.values )
column_list_date_time =[]

# оставляем только те колонки где дата и время
for column in column_list_raw:
    if column[:2].isdigit():
        column_list_date_time.append(column)

# идем по всем значениям по нужным колонкам
lpull_list_values = []
for index, row in excel_file_df.iterrows():
    for column in column_list_date_time:
        strdate = column[:5] + '.' + str(datetime.datetime.now().year)
        strtime = column[-5:]
        fact_value = row[column]
        # print(row['Серийный номер ПУ'])
        abonInfo = get_info_elem_from_registry(rspn_registry_Abon_PU, str(row['Серийный номер ПУ']), 2, strdate)
        poluChasy_id = get_id_catalog_by_value(rspPoluchasyID, strtime)
        if not abonInfo:
            print('нет пересечения абонента и в периоде "Серийный номер ПУ"', str(row['Серийный номер ПУ']))
            serialPU_id = get_id_catalog_by_value(rspSerPU_ID, str(row['Серийный номер ПУ']))
            if not serialPU_id:
                print('вставляем новый ПУ', str(row['Серийный номер ПУ']))
                triafly_conn.put([[str(row['Серийный номер ПУ']),'','']], triaflyRegistr_PU)
                rspSerPU_ID = triafly_conn.get(triaflyReportSerPU_ID)  # заново запрашиваем сериынйе номера
                serialPU_id = get_id_catalog_by_value(rspSerPU_ID, str(row['Серийный номер ПУ']))
                if serialPU_id:
                    print('вставляем пересечение абонента и нового ПУ', str(row['Серийный номер ПУ']))
                    triafly_conn.put([[strdate,'31.12.2099',serialPU_id, '', '']], triaflyRegistr_Abon_PU)
                    rspn_registry_Abon_PU = triafly_conn.get(triaflyRegistr_Abon_PU)  # заново запрашиваем реестр пересечения абонентов и приборов учета по времени
            if serialPU_id:
                listvalue = [''
                            , ''
                            , ''
                            , ''
                            , ''
                            , ''
                            , ''
                            , ''
                            , serialPU_id
                            , strdate
                            , poluChasy_id
                            , fact_value if fact_value >= 0 else ''
                            , 0
                            , 0
                             ]
        else:
            LineAbonentInfo = []
            listvalue=[]
            TransfLineInfo=[]
            TPTransfInfo=[]
            # print('Серийный номер ПУ = ', str(row['Серийный номер ПУ']))
            # print('abonInfo = ', abonInfo)
            if abonInfo[3]:
                LineAbonentInfo = get_info_elem_from_registry(rspn_registry_LineAbonent, abonInfo[3],3, strdate)  # реестр пересечения абонентов и приборов учета по времени
                if LineAbonentInfo:
                    TransfLineInfo = get_info_elem_from_registry(rspn_registry_TransfLine, LineAbonentInfo[2],3, strdate)  # реестр
                if TransfLineInfo:
                    TPTransfInfo = get_info_elem_from_registry(rspn_registry_TPTransf, TransfLineInfo[2], 4, strdate)  # реестр
            else:
                TPTransfInfo = get_info_elem_from_registry(rspn_registry_TPTransf, abonInfo[4],4, strdate)  # реестр пересечения абонентов и приборов учета по времени
                # print('abonInfo[4] = ', abonInfo[4])
                # print('TransfLineInfo = ', TransfLineInfo)
            # print(TransfLineInfo)

            # print('LineAbonentInfo =',LineAbonentInfo)
            # print('TransfLineInfo =', TransfLineInfo)
            # print('TPTransfInfo =', TPTransfInfo)
            # print(datetime.datetime.now(), abonInfo[0])

            # abonInfo[0] Э_с Дата
            # abonInfo[1] Э_по Дата
            # abonInfo[2] серийный номер прибора учета
            # abonInfo[3] абонент
            # abonInfo[4] Э_Трансформатор

            # LineAbonentInfo[0] Э_с Дата
            # LineAbonentInfo[1] Э_по Дата
            # LineAbonentInfo[2] Э_Линия
            # LineAbonentInfo[3] Э_Абонент
            # LineAbonentInfo[4] Мощность по договору

            # TransfLineInfo[0] Э_с Дата
            # TransfLineInfo[1] Э_по Дата
            # TransfLineInfo[2] Э_Трансформатор
            # TransfLineInfo[3] Э_Линия
            # TransfLineInfo[4] Э_АВ линии (автоматический выключатель/рубильник)
            # TransfLineInfo[5] макс. ток, А

            # TPTransfInfo[0] Э_с Дата
            # TPTransfInfo[1] Э_по Дата
            # TPTransfInfo[2] Э_Населенный пункт
            # TPTransfInfo[3] Э_ТП (трансформаторная подстанция)
            # TPTransfInfo[4] Э_Трансформатор
            # TPTransfInfo[5] Э_АВ трансформатора (автоматический выключатель/рубильник)
            # TPTransfInfo[6] макс. ток, А

            # strdate
            # strtime
            # type(fact_value))
            abonent_id = get_id_catalog_by_value(rspAbonentID, abonInfo[3]) # для трансформаторов это поле пустое
            serialPU_id = get_id_catalog_by_value(rspSerPU_ID, abonInfo[2])
            transf_ID = ''
            line_ID = ''
            dogovor_power = ''
            if abonent_id != '':
                line_ID = get_id_catalog_by_value(rspLine_ID, LineAbonentInfo[2])
                transf_ID = get_id_catalog_by_value(rspTransf_ID, TransfLineInfo[2])
                dogovor_power = LineAbonentInfo[4]
            else:
                transf_ID = get_id_catalog_by_value(rspTransf_ID, abonInfo[4])
            #print(' abonInfo[5] = ',  abonInfo[5])
            #print('transf_ID = ', transf_ID)
            #print('abonInfo[0]=',abonInfo[0])

            TransfAV_ID = ''
            tp_id = ''
            nasPunkt_ID = ''
            if TPTransfInfo:
                TransfAV_ID = get_id_catalog_by_value(rspTransfAV_ID, TPTransfInfo[5])
                tp_id = get_id_catalog_by_value(rspTP_ID, TPTransfInfo[3])
                nasPunkt_ID = get_id_catalog_by_value(rspNasPunkt_ID, TPTransfInfo[2])

            LineAV_ID = ''
            if TransfLineInfo:
                LineAV_ID = get_id_catalog_by_value(rspLineAV_ID, TransfLineInfo[4])


            MoreThenP09 = 0
            MoreThenP = 0
            dogovor_power_int = 0
            if dogovor_power != '' :
                dogovor_power_int = int(dogovor_power)
            if fact_value >= 0:
                if dogovor_power_int > 0:
                    if (fact_value >= dogovor_power_int*0.9) and (fact_value <= dogovor_power_int):
                        MoreThenP09 = 1
                    if (fact_value >= dogovor_power_int):
                        MoreThenP = 1

            listvalue = [ nasPunkt_ID
                        , tp_id
                        , transf_ID
                        , TransfAV_ID
                        , line_ID
                        , LineAV_ID
                        , abonent_id
                        , dogovor_power
                        , serialPU_id
                        , strdate
                        , poluChasy_id
                        , fact_value if fact_value >= 0 else ''
                        , MoreThenP09
                        , MoreThenP
                        ]
        # print(listvalue)
        lpull_list_values.append(listvalue)
        if len(lpull_list_values) > 10000:
            #print(lpull_list_values)
            print(datetime.datetime.now(),'Inserting values')
            triafly_conn.put(lpull_list_values, triaflyRegistr_Fact)
            print(datetime.datetime.now(), 'end Inserting values')
            lpull_list_values = []
    #print(row[column])
#print(lpull_list_values)
if len(lpull_list_values) > 0 :
    triafly_conn.put(lpull_list_values, triaflyRegistr_Fact)
#print(column_list_date_time)
#display(rspn_registry_Abon_PU)

# if rspn_registry_Abon_PU.code == 200:
#     for row in rspn_registry_Abon_PU:
#         triafly_conn([],triaflyRegistr_Fact)





# Произведем новую сессию загрузки данных
