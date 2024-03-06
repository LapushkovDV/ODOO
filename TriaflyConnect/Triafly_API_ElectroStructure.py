from netdbclient import Connection
import Triafly_API_DeleteDuplicates
import pandas as pd
from IPython.display import display
import ssl

import datetime



def get_id_catalog_by_value(catalog, value):
    for one_elem in catalog:
        #print("'",one_Abon_PU[0],"'",type(one_Abon_PU[0]),"'", serial,"'", type(serial))#
        if str(one_elem[0]) == str(value):
            #print('EQUAL')
            return one_elem[1]
    return ''

def get_insert_catalog(triafly_conn, catalog_ElectroStructure_df, catalog_ElectroStructure, triaflyRegistr_ElectroStructure, parentid, element_name):
    # header_row = catalog_ElectroStructure_df[(catalog_ElectroStructure_df['prt'].isna())]
    if parentid == '':
        _row = catalog_ElectroStructure_df[
            ((catalog_ElectroStructure_df['prt'].isna()) & (
                    catalog_ElectroStructure_df['Название'] == element_name))]
    else:
        _row = catalog_ElectroStructure_df[
            ((catalog_ElectroStructure_df['prt'] == parentid) & (
                    catalog_ElectroStructure_df['Название'] == element_name))]

    #print('header_row = ', _row)
    print('get_insert_catalog element_name =',element_name)
    #print('get_insert_catalog parentid = ',parentid)
    if _row.empty:  # не нашли элемент
        print('not found, inserting')
        listvalue = [element_name, parentid, '']
        triafly_conn.put([listvalue], triaflyRegistr_ElectroStructure)
        catalog_ElectroStructure_df = triafly_conn.get_set(catalog_ElectroStructure)
        if parentid == '':
            _row = catalog_ElectroStructure_df[
                ((catalog_ElectroStructure_df['prt'].isna()) & (
                            catalog_ElectroStructure_df['Название'] == element_name))]
        else:
            _row = catalog_ElectroStructure_df[
                ((catalog_ElectroStructure_df['prt'] == parentid) & (
                            catalog_ElectroStructure_df['Название'] == element_name))]

    return catalog_ElectroStructure_df, _row['id'].values[0]
def _load_excel_electroStructure_toTriafly(excel_file):
    triafly_url = 'http://194.169.192.155:55556/'
    triafly_api_key = '8EBEA456a6'
    ssl._create_default_https_context = ssl._create_unverified_context
    triafly_conn = Connection(triafly_url, triafly_api_key)

    triaflyRegistr_TypeElemElectr = 2576668 #реестр API Э_тип элемента справочника электросети ID
    triaflyRegistr_ElectroStructure = 2576616 # реестр Э_структура электросети
    catalog_ElectroStructure = 2576576 # справочник Э_структура электросети

    #rspn_TypeElemElectr = triafly_conn.get(triaflyRegistr_TypeElemElectr) ##это реестр серийных номеров приборов учета
    #display(rspn_TypeElemElectr)
    catalog_ElectroStructure_df = triafly_conn.get_set(catalog_ElectroStructure)

    excel_file_df = pd.read_excel(excel_file, skiprows=range(2), dtype='object')
    column_list_raw = list(excel_file_df.columns.values)
    print('column_list_raw =', column_list_raw)

    # сначала пойдем по ячейкам только.. т.к. для трансформаторов какая бубуйня в заполнении
    cells_excel_file_df = excel_file_df[(excel_file_df['Тип ячейки'] == 'Ячейка присоединения')]
    print('cells_excel_file_df =', cells_excel_file_df)
    for index, row in excel_file_df.iterrows():
        # for column in column_list_raw:
        #     print('column ', column, '| value = ',row[column])

        # print('row =', row)
        # print('ПС =',row['ПС'])
        _idParent = ''
        element_name = row['Unnamed: 1']
        catalog_ElectroStructure_df,_idParent = get_insert_catalog(triafly_conn, catalog_ElectroStructure_df, catalog_ElectroStructure,
                       triaflyRegistr_ElectroStructure, _idParent, element_name)

        if str(row['ПС']) != 'nan':
            element_name = row['ПС']
        else:
            element_name = '-'
        catalog_ElectroStructure_df,_idParent = get_insert_catalog(triafly_conn, catalog_ElectroStructure_df, catalog_ElectroStructure,
                       triaflyRegistr_ElectroStructure, _idParent, element_name)

        if str(row['Линия/фидер']) != 'nan':
            element_name = row['Линия/фидер']
        else:
            element_name = '-'
        catalog_ElectroStructure_df,_idParent = get_insert_catalog(triafly_conn, catalog_ElectroStructure_df, catalog_ElectroStructure,
                       triaflyRegistr_ElectroStructure, _idParent, element_name)

        if str(row['ТП']) != 'nan':
            element_name = row['ТП']
        else:
            element_name = '-'
        catalog_ElectroStructure_df,_idParent = get_insert_catalog(triafly_conn, catalog_ElectroStructure_df, catalog_ElectroStructure,
                       triaflyRegistr_ElectroStructure, _idParent, element_name)

        if str(row['Ячейка.3']) != 'nan':
            element_name = row['Ячейка.3']
        else:
            element_name = '-'
        catalog_ElectroStructure_df,_idParent = get_insert_catalog(triafly_conn, catalog_ElectroStructure_df, catalog_ElectroStructure,
                       triaflyRegistr_ElectroStructure, _idParent, element_name)

        if str(row['Серийный номер']) != 'nan':
            element_name = row['Серийный номер']
        else:
            element_name = '-'
        catalog_ElectroStructure_df,_idParent = get_insert_catalog(triafly_conn, catalog_ElectroStructure_df, catalog_ElectroStructure,
                       triaflyRegistr_ElectroStructure, _idParent, element_name)







    # if cur_id = header_row['id'].values[0]
    # print('-----')
    # print('cur_id = ',cur_id)
    # row_1 = catalog_ElectroStructure_df[(catalog_ElectroStructure_df['prt'] == cur_id)]
    # print('row_1 =', row_1)

_load_excel_electroStructure_toTriafly(r'C:\Users\Дмитрий\YandexDisk\Work\Систематика\Энсис АСКУЭ\20240306\Копия Копия Стандартный опросный лист - 2024-03-05T164947.187_test.xlsx')