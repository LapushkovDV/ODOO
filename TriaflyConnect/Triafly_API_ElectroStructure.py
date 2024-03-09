from netdbclient import Connection
import Triafly_API_DeleteDuplicates
import pandas as pd
from IPython.display import display
import ssl

import datetime
import re


def get_id_catalog_by_value(catalog, value):
    for one_elem in catalog:
        #print("'",one_Abon_PU[0],"'",type(one_Abon_PU[0]),"'", serial,"'", type(serial))#
        if str(one_elem[0]) == str(value):
            #print('EQUAL')
            return one_elem[1]
    return ''
def getnamecatalogtosearch(registry_ElectroStructure_df, parentid, element_name):
    if parentid == '':
        _row = registry_ElectroStructure_df[
            ((registry_ElectroStructure_df['Э_Структура электросети'].isna()) & (
                    registry_ElectroStructure_df['Э_структура электросети варианты названия в опросном листе'].str.contains(element_name)))]
    else:
        _row = registry_ElectroStructure_df[
            ((registry_ElectroStructure_df['Э_Структура электросети'] == parentid) & (
                    registry_ElectroStructure_df['Э_структура электросети варианты названия в опросном листе'].str.contains(element_name)))]
    if _row.empty:
        return element_name, False
    else:
        return _row['Название'].values[0], True

def get_insert_catalog(triafly_conn, catalog_ElectroStructure_df, registry_ElectroStructure_df, catalog_ElectroStructure, triaflyRegistr_ElectroStructure, parentid, element_name,id_type_element):
    # header_row = catalog_ElectroStructure_df[(catalog_ElectroStructure_df['prt'].isna())]
    element_name, isfound = getnamecatalogtosearch(registry_ElectroStructure_df, parentid, element_name)
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
        listvalue = [element_name, parentid, id_type_element, element_name]
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

def get_insert_catalog_like(triafly_conn, catalog_ElectroStructure_df, registry_ElectroStructure_df, catalog_ElectroStructure, triaflyRegistr_ElectroStructure, parentid, element_name, element_name_like, id_type_element):
    # header_row = catalog_ElectroStructure_df[(catalog_ElectroStructure_df['prt'].isna())]
    element_name, isfound = getnamecatalogtosearch(registry_ElectroStructure_df, parentid, element_name)
    if parentid == '':
        _row = catalog_ElectroStructure_df[
            ((catalog_ElectroStructure_df['prt'].isna()) & (
                    catalog_ElectroStructure_df['Название'].str.contains(element_name_like)))]
    else:
        _row = catalog_ElectroStructure_df[
            ((catalog_ElectroStructure_df['prt'] == parentid) & (
                    catalog_ElectroStructure_df['Название'].str.contains(element_name_like)))]

    #print('header_row = ', _row)
    print('get_insert_catalog element_name =',element_name, 'element_name_like =',element_name_like)

    #print('get_insert_catalog parentid = ',parentid)
    if _row.empty:  # не нашли элемент
        print('not found, inserting')
        listvalue = [element_name, parentid, id_type_element,element_name]
        triafly_conn.put([listvalue], triaflyRegistr_ElectroStructure)
        catalog_ElectroStructure_df = triafly_conn.get_set(catalog_ElectroStructure)
        if parentid == '':
            _row = catalog_ElectroStructure_df[
                ((catalog_ElectroStructure_df['prt'].isna()) & (
                    catalog_ElectroStructure_df['Название'].str.contains(element_name_like)))]
        else:
            _row = catalog_ElectroStructure_df[
                ((catalog_ElectroStructure_df['prt'] == parentid) & (
                    catalog_ElectroStructure_df['Название'].str.contains(element_name_like)))]

    return catalog_ElectroStructure_df, _row['id'].values[0]
def getIdTransUnderTP_withThisCell(catalog_ElectroStructure_df, registry_ElectroStructure_df, _idParent, element_name, typeelemtranf):
    # print('-------def getIdTransUnderTP_withThisCell(  _idParent=',_idParent)
    # print('-------def getIdTransUnderTP_withThisCell(  typeelemtranf=',typeelemtranf)
    # print('-------def getIdTransUnderTP_withThisCell(  element_name = ', element_name)
    typeelemtranf = int(typeelemtranf)
    trnsformator_df = catalog_ElectroStructure_df[
        ((catalog_ElectroStructure_df['prt'] == _idParent) & (
                catalog_ElectroStructure_df['Э_тип элемента справочника электросети'] == typeelemtranf))]
    # trnsformator_df = catalog_ElectroStructure_df[
    #     (catalog_ElectroStructure_df['prt'] == _idParent)]

    # display(trnsformator_df)
    for index, row in trnsformator_df.iterrows():
        id = row['id']
        # print('Э_тип элемента справочника электросети = ',row['Э_тип элемента справочника электросети'])
        element_name_1, isFound = getnamecatalogtosearch(registry_ElectroStructure_df, id, element_name)
        if isFound == True:
            # print('isFound == True')
            return id
    return _idParent



def _load_excel_electroStructure_toTriafly(excel_file):
    triafly_url = 'http://194.169.192.155:55556/'
    triafly_api_key = '8EBEA456a6'
    ssl._create_default_https_context = ssl._create_unverified_context
    triafly_conn = Connection(triafly_url, triafly_api_key)

    triaflyRegistr_TypeElemElectr = 2576668 #реестр API Э_тип элемента справочника электросети ID
    triaflyRegistr_ElectroStructure = 2576616 # реестр Э_структура электросети
    catalog_ElectroStructure = 2576576 # справочник Э_структура электросети

    rspn_TypeElemElectr = triafly_conn.get(triaflyRegistr_TypeElemElectr) ##это Э_тип элемента справочника электросети ID
    display(rspn_TypeElemElectr)
    catalog_ElectroStructure_df = triafly_conn.get_set(catalog_ElectroStructure)

    # column_list_raw = list(catalog_ElectroStructure_df.columns.values)
    # print('catalog_ElectroStructure_columns = ',column_list_raw)
    # for index, row in catalog_ElectroStructure_df.iterrows():
    #     for column in column_list_raw:
    #         print('catalog_ElectroStructure column ', column, '| value = ',row[column])

    registry_ElectroStructure_df = triafly_conn.get_registry(triaflyRegistr_ElectroStructure)

    # column_list_raw = list(registry_ElectroStructure_df.columns.values)
    # print('registry_ElectroStructure_df_columns = ',column_list_raw)
    # for index, row in registry_ElectroStructure_df.iterrows():
    #     for column in column_list_raw:
    #         print('registry_ElectroStructure_df column ', column, '| value = ',row[column])

    excel_file_df = pd.read_excel(excel_file, skiprows=range(2), dtype='object')
    column_list_raw = list(excel_file_df.columns.values)
    print('column_list_raw =', column_list_raw)

    # cells_excel_file_df = excel_file_df[(excel_file_df['Тип ячейки'] == 'Ячейка присоединения')] # сначала пойдем по ячейкам только.. т.к. для трансформаторов какая бубуйня в заполнении
    # print('cells_excel_file_df =', cells_excel_file_df)
    for index, row in excel_file_df.iterrows():
        # for column in column_list_raw:
        #     print('column ', column, '| value = ',row[column])

        # print('row =', row)
        # print('ПС =',row['ПС'])
        _idParent = ''
        # ['ПЭС', '2576583']
        id_type_element = get_id_catalog_by_value(rspn_TypeElemElectr, 'ПЭС')
        element_name = row['Unnamed: 1']
        catalog_ElectroStructure_df,_idParent = get_insert_catalog(triafly_conn, catalog_ElectroStructure_df,registry_ElectroStructure_df, catalog_ElectroStructure,
                       triaflyRegistr_ElectroStructure, _idParent, element_name,id_type_element)

        #['ПС', '2576584'],
        id_type_element = get_id_catalog_by_value(rspn_TypeElemElectr, 'ПС')
        if str(row['ПС']) != 'nan':
            element_name = row['ПС']
        else:
            element_name = '-'
        catalog_ElectroStructure_df,_idParent = get_insert_catalog(triafly_conn, catalog_ElectroStructure_df, registry_ElectroStructure_df,catalog_ElectroStructure,
                       triaflyRegistr_ElectroStructure, _idParent, element_name, id_type_element)

        #'Линия/фидер', '2576585']
        id_type_element = get_id_catalog_by_value(rspn_TypeElemElectr, 'Линия/фидер')
        if str(row['Линия/фидер']) != 'nan':
            element_name = row['Линия/фидер']
        else:
            element_name = '-'

        if element_name == 'ф. 5': # пошел костыль на кривой EXCEL
            if str(row['ТП']) != 'nan':
                tp_name = row['ТП']
                nums = re.findall(r'\b\d+\b', tp_name)
                if nums:
                    tp_name_like = str(nums[0])
                    if tp_name_like == '11004':
                        element_name = 'ф. 15'

        catalog_ElectroStructure_df,_idParent = get_insert_catalog(triafly_conn, catalog_ElectroStructure_df,registry_ElectroStructure_df, catalog_ElectroStructure,
                       triaflyRegistr_ElectroStructure, _idParent, element_name, id_type_element)

        #['ТП', '2576586']
        id_type_element = get_id_catalog_by_value(rspn_TypeElemElectr, 'ТП')
        # element_name_like = ''
        if str(row['ТП']) != 'nan':
            element_name = row['ТП']
        else:
            element_name = '-'
        # if element_name_like != '':
        #     catalog_ElectroStructure_df,_idParent = get_insert_catalog_like(triafly_conn, catalog_ElectroStructure_df, registry_ElectroStructure_df, catalog_ElectroStructure,
        #                    triaflyRegistr_ElectroStructure, _idParent, element_name, element_name_like,id_type_element)
        # else:
        #     catalog_ElectroStructure_df,_idParent = get_insert_catalog(triafly_conn, catalog_ElectroStructure_df, registry_ElectroStructure_df,catalog_ElectroStructure,
        #                    triaflyRegistr_ElectroStructure, _idParent, element_name,id_type_element)
        catalog_ElectroStructure_df,_idParent = get_insert_catalog(triafly_conn, catalog_ElectroStructure_df, registry_ElectroStructure_df,catalog_ElectroStructure,
                       triaflyRegistr_ElectroStructure, _idParent, element_name,id_type_element)

        id_type_element = get_id_catalog_by_value(rspn_TypeElemElectr, 'Ячейка')
        if str(row['Тип ячейки.3']) != 'nan':
            if str(row['Тип ячейки.3']) == 'Ячейка нижней обмотки силового трансформатора':
                id_type_element = get_id_catalog_by_value(rspn_TypeElemElectr, 'Трансформатор')

        #  ['Трансформатор', '2578734'], ['Ячейка', '2576587']
        if str(row['Ячейка.3']) != 'nan':
            element_name = row['Ячейка.3']
            # print('********** element_name = ', element_name)
            _idParent = getIdTransUnderTP_withThisCell(catalog_ElectroStructure_df, registry_ElectroStructure_df,
                                                       _idParent, element_name,
                                                       get_id_catalog_by_value(rspn_TypeElemElectr, 'Трансформатор') )
        else:
            element_name = '-'

        catalog_ElectroStructure_df,_idParent = get_insert_catalog(triafly_conn, catalog_ElectroStructure_df, registry_ElectroStructure_df, catalog_ElectroStructure,
                       triaflyRegistr_ElectroStructure, _idParent, element_name, id_type_element)

        # ['Серийный номер ПУ', '2576588'],
        id_type_element = get_id_catalog_by_value(rspn_TypeElemElectr, 'Серийный номер ПУ')
        if str(row['Серийный номер']) != 'nan':
            element_name = row['Серийный номер']
        else:
            element_name = '-'
        catalog_ElectroStructure_df,_idParent = get_insert_catalog(triafly_conn, catalog_ElectroStructure_df,registry_ElectroStructure_df, catalog_ElectroStructure,
                       triaflyRegistr_ElectroStructure, _idParent, element_name, id_type_element)

    # if cur_id = header_row['id'].values[0]
    # print('-----')
    # print('cur_id = ',cur_id)
    # row_1 = catalog_ElectroStructure_df[(catalog_ElectroStructure_df['prt'] == cur_id)]
    # print('row_1 =', row_1)


_load_excel_electroStructure_toTriafly(r'C:\Users\Дмитрий\YandexDisk\Work\Систематика\Энсис АСКУЭ\20240306\Копия Стандартный опросный лист - 2024-03-05T164947.187.xlsx')