# -*- encoding: utf-8 -*-

try :                           # python2
    from urllib import quote_plus , urlencode
    import urllib2
    import urlparse
except ImportError :            # python3
    from urllib.parse import quote_plus , urlencode
    import urllib.request as urllib2
    import urllib.parse as urlparse

try :
    import requests
except ImportError :
    requests = None

import collections
import json
import xml.etree.ElementTree as ET

import pandas as pd

class Response ( list ) :
    def __init__ ( self , response , code ) :
        self.code = code
        self.xml = response.read ()
        self.tree = ET.fromstring ( self.xml )
        if code == 200 :
            self.params = [ e.text for e in self.tree[0] ]
            self.extend ( [ c.text for c in r ] for r in self.tree[1] )
        else :                  # make it readable
            self.xml = ET.tostring (
                self.tree , encoding='utf-8' ).decode ( 'utf-8' )

class Connection ( object ) :

    def __init__ ( self , url , api_key , **kwargs ) :
        self.open_kwargs = kwargs.pop ( 'urlopen' , {} )
        self.veryfy = kwargs.pop ( 'veryfy' , True )
        self.default_format = kwargs.pop ( 'default_format' , 'pandas' )
        self.request_kwargs = kwargs
        self.url = url
        self.api_key = api_key
        self.obj_name_cache = {}
        self._blocks = None

    def get ( self , report_id , params=None ) :
        url = urlparse.urljoin ( self.url , 'api/1/%d/' % report_id )
        if params is not None :
            url += '?' + '&'.join ( 'param='+quote_plus(param)
                                    for param in params )
        request = urllib2.Request ( url , **self.request_kwargs )
        request.add_header ( 'Netdb-Api-Key' , self.api_key )
        try : response = urllib2.urlopen ( request , **self.open_kwargs )
        except urllib2.HTTPError as httperror :
            return Response ( httperror , httperror.code )
        return Response ( response , 200 )

    def put ( self , data , report_id , params=None ) :
        e_data = ET.Element ( 'data' )
        if params is not None :
            e_params = ET.SubElement ( e_data , 'params' )
            for p in params :
                e_param = ET.SubElement ( e_params , 'param' )
                e_param.text = str ( p )
        table = ET.SubElement ( e_data , 'table' )
        for row in data :
            tr = ET.SubElement ( table , 'tr' )
            for v in row :
                td = ET.SubElement ( tr , 'td' )
                td.text = str ( v )
        data = ET.tostring ( e_data , encoding='utf-8' )
        data = urlencode ( { 'data' : data } ).encode ( 'ascii' )
        url = urlparse.urljoin ( self.url , 'api/1/%d/' % report_id )
        request = urllib2.Request ( url , **self.request_kwargs )
        request.add_header ( 'Netdb-Api-Key' , self.api_key )
        response = urllib2.urlopen ( request , data , **self.open_kwargs )
        if response.getcode() != 200 : return response.read ()
        response = ET.fromstring ( response.read() )
        return int(response.attrib['updated']) , \
            int(response.attrib['created']) , int(response.attrib['deleted'])

    #============= API3 ================

    def set_default_format ( self , format ) :
        assert format in ( 'pandas' , 'raw' , 'str' )
        res = self.default_format
        self.default_format = format
        return res

    def add_to_set ( self , id_or_name , ids ) :
        ids = list ( ids )
        set_id = self._id_from_id_or_name ( id_or_name , 'sets' )
        data = json.dumps ( [ set_id , ids ] )
        data = urlencode ( { 'data' : data } ).encode ( 'ascii' )
        res = self._get_json ( 'add_to_set' , data )
        return res

    def delete_from_set ( self , id_or_name , ids ) :
        ids = list ( ids )
        set_id = self._id_from_id_or_name ( id_or_name , 'sets' )
        data = json.dumps ( [ set_id , ids ] )
        data = urlencode ( { 'data' : data } ).encode ( 'ascii' )
        res = self._get_json ( 'delete_from_set' , data )
        return res

    def delete_objects ( self , ids ) :
        ids = list ( ids )
        data = json.dumps ( ids )
        data = urlencode ( { 'data' : data } ).encode ( 'ascii' )
        res = self._get_json ( 'delete_objects' , data )
        if res is None : self.reset_blocks ()
        return res

    def create_objects ( self , data, files=None ) :
        data = list ( data )
        data = [ { self._id_from_id_or_name(k,'descriptors') : _to_json(v)
                   for k , v in d.items() }
                 for d in data ]
        data = json.dumps ( data )
        if files :
            response = self._get_requests_url (
                'create_objects' , { 'data' : data } , files )
            res = response.json ()
        else :
            data = urlencode ( { 'data' : data } ).encode ( 'ascii' )
            res = self._get_json ( 'create_objects' , data )
        if isinstance ( res, list ) : self.reset_blocks ()
        return res

    def update_objects ( self , data, files=None ) :
        data = dict ( data )
        data = { kk : { self._id_from_id_or_name(k,'descriptors') : _to_json(v)
                          for k , v in vv.items() }
                 for kk , vv in data.items() }
        data = json.dumps ( data )
        if files :
            response = self._get_requests_url (
                'update_objects' , { 'data' : data } , files )
            res = response.json ()
        else :
            data = urlencode ( { 'data' : data } ).encode ( 'ascii' )
            res = self._get_json ( 'update_objects' , data )
        return res

    def create_descriptor ( self , name , type , choice=None , related=None ,
                            groups=None ) :
        if isinstance ( type , str ) : type = descriptor_types [ type ]
        assert type in descriptor_types.values()
        if choice is not None :
            choice = self._id_from_id_or_name ( choice , 'sets' )
        if related is not None :
            related = [ self._id_from_id_or_name(d,'descriptors')
                        for d in related ]
        if groups is not None :
            G = self.get_set ( -96 )
            G = dict ( zip(G['Название'],G.id) )
            groups = [ G[g] if isinstance(g,str) else g
                       for g in groups ]
            assert all ( g in G.values() for g in groups )
        data = dict ( name=name , type=type , choice=choice , related=related ,
                      groups=groups )
        data = json.dumps ( data )
        data = urlencode ( { 'data' : data } ).encode ( 'ascii' )
        res = self._get_json ( 'create_descriptor' , data )
        if isinstance ( res , int ) : self.reset_sets ()
        return res

    def create_set ( self , name ) :
        assert name not in self.sets_by_name
        data = urlencode ( { 'data' : name } ).encode ( 'ascii' )
        res = self._get_json ( 'create_set' , data )
        if isinstance ( res , int ) : self.reset_sets ()
        return res

    def __getattr__ ( self , name ) :
        if name not in SETS and \
           not ( name.endswith('_by_name') and name[:-8] in SETS ) :
            raise AttributeError
        self.reset ()
        return getattr ( self , name )

    def _get_request ( self, url ):
        url = urlparse.urljoin ( self.url , 'api/3/' + url )
        request = urllib2.Request ( url , **self.request_kwargs )
        request.add_header ( 'Netdb-Api-Key' , self.api_key )
        return request

    def _get_url ( self , url , data=None ) :
        request = self._get_request ( url )
        return urllib2.urlopen ( request , data , **self.open_kwargs )

    def _get_requests_url ( self, url, data=None, files=None ):
        if not requests : raise ImportError ( 'requests required' )
        request = self._get_request ( url )
        r = requests.post (
            request.full_url,
            data=data,
            files=files,
            headers=request.headers,
            verify=self.veryfy )
        return r

    @property
    def blocks ( self ) :
        if self._blocks is None : self.reset ()
        return self._blocks

    def reset ( self ) :
        self.reset_blocks ()
        self.reset_sets ()
        self.obj_name_cache = {}

    def reset_sets ( self ) :
        for n , (c,t) in SETS.items() :
            by_id , by_name = self._get_set ( n , c , t )
            setattr ( self , n , by_id )
            setattr ( self , n+'_by_name' , by_name )

    def reset_blocks ( self ) :
        res = self._get_json ( 'blocks' )
        try : res = res [ 'data' ] [ 'reportData' ] [ 'data' ]
        except KeyError : return # считается асинхронно, может недосчиталось
        b = []
        for r in res :
            b.append ( Block( *[ rr.get('calc_value')
                                 for rr in r[:len(Block._fields)] ] ) )
        self._blocks = b

    def _get_set ( self , command , columns , type ) :
        res = self._get_json ( command )
        by_id = {}
        by_name = {}
        for d in res :
            kwargs = { columns[k] : d.get(k) for k in columns }
            by_name [ d['-3'] ] = by_id [ d['id'] ] = type ( **kwargs )
        return by_id , by_name

    def _to_pandas ( self , json ) :
        res = pd.DataFrame ( json )
        try : res = res.rename ( index=res.id.get , columns=self._cname )
        except AttributeError : pass # empty
        return res

    def _to_str ( self , json ) :
        return self._to_pandas ( [ self._row_to_str(r) for r in json ] )

    def _row_to_str ( self , row ) :
        return dict ( ( k , self._cell_to_str(v,k) ) for k , v in row.items() )

    def _cell_to_str ( self , value , key=None ) :
        if key == 'id' : return value
        try : d = self.descriptors [ int(key) ]
        except ( ValueError , KeyError ) : return value
        if d.type == descriptor_types['Справочник'] :
            return self._set_element_name ( d.choice , value )
        elif d.type == descriptor_types['Период'] :
            return period2str ( value )
        elif d.type == descriptor_types['Множество значений из справочника'] :
            return self._set_element_names ( d.choice , value )
        elif d.type == descriptor_types['Тип множество периодов'] :
            return ', '.join ( period2str(v) for v in value )
        return value

    def _set_element_name ( self , set_id , obj_id ) :
        try : return self.obj_name_cache [ obj_id ]
        except KeyError : pass
        s = self.get_set ( set_id , format='raw' )
        for row in s :
            try : self.obj_name_cache [ row['id'] ] = row [ '-3' ]
            except KeyError : self.obj_name_cache [ row['id'] ] = row [ 'id' ]
        try : return self.obj_name_cache [ obj_id ]
        except KeyError : self.obj_name_cache [ obj_id ] = obj_id
        return obj_id

    def _set_element_names ( self , set_id , subset_ids ) :
        return ', '.join ( self._set_element_name(set_id,id)
                           for id in subset_ids )

    def get_internal_set ( self , id , format=None ) :
        url = 'set/{0}'.format ( id )
        res = self._get_json ( url )
        format = format or self.default_format
        if format == 'raw' : return res
        if format == 'pandas' : return self._to_pandas ( res )
        return self._to_str ( res )

    def get_set ( self , id_or_name , format=None ) :
        id = self._id_from_id_or_name ( id_or_name , 'sets' )
        return self.get_internal_set ( id , format )

    def _cname ( self , cid ) :
        try : return self.descriptors [ int(cid) ].name
        except ( ValueError , KeyError ) : return cid

    def _params2data ( self , params ) :
        if params is None : return None
        for p in params :
            p['param_id'] = self._id_from_id_or_name (
                p['param_id'] , 'descriptors' )
            if 'param_index' not in p:
                p['param_index'] = 0
        data = { 'with_params': json.dumps ( params ) }
        data = urlencode ( data ).encode ( 'ascii' )
        return data

    def get_report ( self , id_or_name , params=None , format=None ) :
        id = self._id_from_id_or_name ( id_or_name , 'reports' )
        url = 'report/{0}'.format(id)
        return self._get_and_process_response_data (
            url , format or self.default_format , params)

    def get_form ( self , id_or_name , params=None , format=None ) :
        id = self._id_from_id_or_name ( id_or_name , 'forms' )
        url = 'report/{0}'.format(id)
        return self._get_and_process_response_data (
            url , format or self.default_format , params)

    def get_registry ( self , id_or_name , params=None , format=None ) :
        id = self._id_from_id_or_name ( id_or_name , 'registries' )
        url = 'registry/{0}'.format(id)
        return self._get_and_process_response_data (
            url , format or self.default_format , params)

    def get_file (self , file_name , buffer ):
        url = urlparse.urljoin ( self.url , '/media/' + file_name )
        request = urllib2.Request ( url , **self.request_kwargs )
        request.add_header ( 'Netdb-Api-Key' , self.api_key )
        r = urllib2.urlopen ( request , **self.open_kwargs )
        while True :
            chunk = r.read ( 8192 )
            if chunk : buffer.write ( chunk )
            else : break

    def _get_json ( self , url , data=None ) :
        response = self._get_url ( url , data )
        res = response.read ()
        res = json.loads ( res )
        return res

    def _get_and_process_parameters ( self , url , format=None ) :
        res = self._get_json ( url )
        format = format or self.default_format
        if format == 'raw' : return res
        if format == 'str' :
            for row in res :
                try : d = self.descriptors [ row['id'] ]
                except KeyError : continue
                row [ '-3' ] = d.name
                default = row [ 'default' ]
                row [ 'default' ] = [
                    self._cell_to_str(v,d.id) for v in default ] \
                    if isinstance ( default , list ) \
                    else self._cell_to_str ( default , d.id )
        return self._to_pandas ( res )

    def _get_and_process_response_data ( self , url , format=None ,
                                         params=None ) :
        data = self._params2data ( params )
        res = self._get_json ( url , data )
        format = format or self.default_format
        if format == 'raw' : return res
        data = [ [ cell.get('calc_value') or cell.get('db_value')
                   for cell in row ]
                 for row in res['data']['reportData']['data'] ]

        # объекты ячеек:
        objs = [ [ cell.get('obj') for cell in row ]
                 for row in res['data']['reportData']['data'] ]

        def maxdepth ( h ) :
            try : return max ( 1 if 'children' not in i
                               else i.get('group_children',0) +
                               maxdepth(i['children'])
                               for i in h )
            except ValueError : return 1

        def ind_tuples ( h , maxdepth ) :
            for i in h :
                if 'children' in i :
                    if not i.get('group_children') :
                        yield (i['display_title'],) + ('',)*(maxdepth-1)
                        yield from ind_tuples ( i['children'] , maxdepth )
                    else :
                        for k in ind_tuples ( i['children'] , maxdepth-1 ) :
                            yield (i['display_title'],) + k
                else :
                    yield (i['display_title'],) + ('',)*(maxdepth-1)
        def ind ( h ) :
            m = maxdepth ( h )
            if m == 1 : return [ i[0] for i in ind_tuples(h,1) ]
            return pd.MultiIndex.from_tuples ( ind_tuples(h,m) )

        # м.б. отчето-реестр или реестр:
        if 'row_header' not in res['headers']['reportHeaders'] :
            # проверяем возможность конструирования индекса из objs:
            idx = []
            for r in objs :
                ri = None       # кандидат на индекс строки
                for c in r :
                    if c is None : continue
                    if ri is None : ri = c # нашли первый не пустой
                    elif ri != c : break   # нашли второй не равный первому
                else :
                    if ri is not None : # нашли единственный кандидат
                        idx.append ( ri )
                        continue
                break           # все плохо
            if len(set(idx)) != len(data) : idx = range(len(data))

            res['headers']['reportHeaders']['row_header'] = [
                { 'display_title' : i } for i in idx ]

        if format == 'str' :
            if 'descriptors_list' in res['headers'] :
                d = res['headers']['descriptors_list']
                def str_row_column ( row , column , value ) :
                    return self._cell_to_str ( value , d[column][-1] )
            elif 'colsDescrsMeta' in res['headers'] :
                d = res['headers']['colsDescrsMeta']
                def str_row_column ( row , column , value ) :
                    return self._cell_to_str ( value , d[column]['descr'] )
            else :
                assert 'rowsDescrsMeta' in res['headers']
                d = res['headers']['rowsDescrsMeta']
                def str_row_column ( row , column , value ) :
                    return self._cell_to_str ( value , d[row]['descr'] )
            for rn , row in enumerate ( data ) :
                for cn , column in enumerate ( row ) :
                    row[cn] = str_row_column ( rn , cn , row[cn] )

        return pd.DataFrame (
            data , index=ind(res['headers']['reportHeaders']['row_header']) ,
            columns=ind(res['headers']['reportHeaders']['col_header']) )


    def get_registry_parameters ( self , id_or_name , format=None ) :
        id = self._id_from_id_or_name ( id_or_name , 'registries' )
        url = 'registry-parameters/{0}'.format ( id )
        return self._get_and_process_parameters ( url , format )

    def get_report_parameters ( self , id_or_name , format=None ) :
        id = self._id_from_id_or_name ( id_or_name , 'reports' )
        url = 'registry-parameters/{0}'.format ( id )
        return self._get_and_process_parameters ( url , format )

    def get_form_parameters ( self , id_or_name , format=None ) :
        id = self._id_from_id_or_name ( id_or_name , 'forms' )
        url = 'registry-parameters/{0}'.format ( id )
        return self._get_and_process_parameters ( url , format )

    def _id_from_id_or_name ( self , id_or_name , by_id_name ) :
        by_id = getattr ( self , by_id_name )
        by_name = getattr ( self , by_id_name+'_by_name' )
        id = id_or_name
        if isinstance ( id , str ) :
            id = by_name [ id_or_name ].id
        assert id in by_id
        return id

    def get_block ( self , block_or_descrs_list , format=None ,
                    extra_descrs_list=None , from_set=None ) :
        if isinstance ( block_or_descrs_list , Block ) :
            from_set = from_set or block_or_descrs_list.set_id
            block_or_descrs_list = block_or_descrs_list.descriptors
        block_or_descrs_list = [ self._id_from_id_or_name(d,'descriptors')
                                 for d in block_or_descrs_list ]
        extra_descrs_list = [ self._id_from_id_or_name(d,'descriptors')
                              for d in (extra_descrs_list or []) ]
        if from_set : from_set = self._id_from_id_or_name ( from_set , 'sets' )
        url = 'block/?descrs={0}'.format (
            ','.join(str(d) for d in block_or_descrs_list) )
        if extra_descrs_list :
            url += '&extra={0}'.format (
            ','.join(str(d) for d in extra_descrs_list) )
        if from_set : url += '&set_id={0}'.format ( from_set )
        res = self._get_json ( url )
        format = format or self.default_format
        if format == 'raw' : return res
        columns = block_or_descrs_list + extra_descrs_list # спереди еще id
        if format == 'str' :
            for row in res :
                for ri , ( d , v ) in enumerate ( zip(columns,row[1:]) , 1 ) :
                    row[ri] = self._cell_to_str ( v , d )
        res = pd.DataFrame (
            res , columns=['id']+[self._cname(id) for id in columns] )
        res = res.rename ( index=res.id.get )
        return res


DESCRIPTORS_COLUMNS = { 'id' : 'id' ,
                        'model' : 'model' ,
                        '-3' : 'name' ,
                        '-22' : 'type' ,
                        '-124' : 'related_descriptors' ,
                        '-26' : 'choice' ,
                        '-107' : 'auto' ,
                        '-29' : 'description' ,
                        '-292' : 'ignored_in_calculations' ,
                        }

SET_COLUMNS = { 'id' : 'id' ,
                '-3' : 'name' ,
                }

Descriptor = collections.namedtuple ( 'Descriptor' ,
                                      DESCRIPTORS_COLUMNS.values() )

Set = collections.namedtuple ( 'Set' , SET_COLUMNS.values() )

Block = collections.namedtuple ( 'Block' , [ 'descriptors' ,
                                             'related_descriptors' , 'set_id' ,
                                             'total' ] )
SETS =  {
    'descriptors' : ( DESCRIPTORS_COLUMNS , Descriptor ) ,
    'forms' : ( SET_COLUMNS , Set ) ,
    'reports' : ( SET_COLUMNS , Set ) ,
    'registries' : ( SET_COLUMNS , Set ) ,
    'sets' : ( SET_COLUMNS , Set ) ,
}

descriptor_types = {
    'Тип множество периодов' : -47 ,
    'Число' : -37 ,
    'Период' : -42 ,
    'Да/Нет' : -40 ,
    'Целое' : -35 ,
    'Множественный файл' : -46 ,
    'Дата и время' : -41 ,
    'Денежный' : -1100 ,
    'Неотрицательное' : -36 ,
    'Множество значений из справочника' : -44 ,
    'Строка' : -34 ,
    'Множественное отношение между справочниками' : -48 ,
    'Справочник' : -38 ,
    'Файл' : -43 ,
    }

def _to_json ( value ) :
    return ','.join(str(v) for v in value) if isinstance(value,(list,tuple)) \
        else value

############################################################
#                         Периоды                          #
############################################################

period_day = -59           # виды периодов
period_week = -58
period_decade = -57        # декада
period_month = -56
period_quarter = -55
period_halfyear = -54      # полугодие
period_3quarters = -53     # 3 квартала, или 9 месяцев, или 3/4 года
period_year = -52

period_code_by_name = { '3 quarters' : period_3quarters ,
                        '3 квартала' : period_3quarters ,
                        'day' : period_day ,
                        'week' : period_week ,
                        'decade' : period_decade ,
                        'month' : period_month ,
                        'quarter' : period_quarter ,
                        'halfyear' : period_halfyear ,
                        'year' : period_year ,
                        'день' : period_day ,
                        'неделя' : period_week ,
                        'декада' : period_decade ,
                        'месяц' : period_month ,
                        'квартал' : period_quarter ,
                        'полугодие' : period_halfyear ,
                        'год' : period_year , }

period_name_by_code = dict (    # сортируем чтоб по русски
    (v,k) for k,v in sorted(period_code_by_name.items()) )

def period2str ( s ) :
    try : p = Period.deserialize ( s )
    except TypeError : return s
    return p.to_string ()

datetime_format = '%Y-%m-%d %H:%M:%S'
def period ( datetime , type ) :
    """ Netdb period by datetime and period type

    :datetime: datetime, period start
    :type: string, one of: 'day', 'week', 'decade', 'month', 'quarter',
       '3 quarters', 'halfyear', 'year', 'день', 'неделя', 'декада',
       'месяц', 'квартал', '3 квартала', 'полугодие', 'год'
    """
    return datetime.strftime(datetime_format)+'|'+str(period_code_by_name[type])

def rperiod ( offset , type ) :
    """ Netdb relative period by offset and period type

    :offset: integer,
    :type: string, one of: 'day', 'week', 'decade', 'month', 'quarter',
       '3 quarters', 'halfyear', 'year', 'день', 'неделя', 'декада',
       'месяц', 'квартал', '3 квартала', 'полугодие', 'год'
    """
    return str(offset)+'|'+str(period_code_by_name[type])

# дальше поправленный код из netdb.periods:

import re, logging
from datetime import date, datetime, timedelta
import copyreg

class tzutils :
    MIN = datetime(1900,1,1)
    MAX = datetime(9000,1,1)
    @staticmethod
    def dt ( d ) : return d
def Obj ( v ) : return v
def _ ( v ) : return v

WEEK_AS_MONTHS_CHILD = False
def set_week_as_months_child ( v ) :
    global WEEK_AS_MONTHS_CHILD
    res = WEEK_AS_MONTHS_CHILD
    WEEK_AS_MONTHS_CHILD = v
    return res

# типы периодов от меньшего к большему
PERIOD_TYPES = [period_day, period_week, period_decade, period_month,
                period_quarter, period_halfyear, period_3quarters, period_year]
# "Странные" типы периодов - они являются не единственными родителями,
# и не имеют родителей - если в отчете их нет в явном виде, то иерархия
# периодов представляет нормальное дерево.
# Также важно, чтобы они шли последними среди родителей
MULTI_PARENT_PERIOD_TYPES = set([
    period_week, period_3quarters])


PERIOD_END_GETTERS = {
    period_day: lambda period: period.start + timedelta(1),
    period_week: lambda period: period.start + timedelta(7),
    period_decade: lambda period: period.start + timedelta(10) if
        period.start.day in (1, 11) else add_months(
        tzutils.dt(datetime(period.start.year, period.start.month, 1)), 1),
    period_month: lambda period: add_months(period.start, 1),
    period_quarter: lambda period: add_months(period.start, 3),
    period_halfyear: lambda period: add_months(period.start, 6),
    period_3quarters: lambda period: add_months(period.start, 9),
    period_year: lambda period: tzutils.dt(datetime(period.start.year + 1,
        period.start.month, period.start.day)),
}


# дистанция между первым и вторым периодами (со знаком)
# одного типа в единицах этого периода:
PERIOD_DIST = {
    period_day : lambda s,f : ( f.start - s.start ).days ,
    period_week : lambda s,f : ( f.start - s.start ).days // 7 ,
    period_decade : lambda s,f : ( f.start - s.start ).days // 10 ,
    period_month : lambda s,f : ( (f.start.year-s.start.year)*12 +
                                  f.start.month-s.start.month ) ,
    period_quarter : lambda s,f : ( (f.start.year-s.start.year)*12 +
                                    f.start.month-s.start.month ) // 3 ,
    period_halfyear : lambda s,f : ( (f.start.year-s.start.year)*12 +
                                     f.start.month-s.start.month ) // 6 ,
    period_3quarters : lambda s,f : ( (f.start.year-s.start.year)*12 +
                                     f.start.month-s.start.month ) // 9 ,
    period_year: lambda s,f : f.start.year - s.start.year ,
}


def add_months(date, months):
    return tzutils.dt(datetime(date.year + (date.month + months) // 13,
        ((date.month + months) % 12) or 12, date.day))


_period_string_cache = {} # ключ - нормализованая строка
_period_cache = {} # ключ - (начало периода, тип периода)
# кэшируем потому что периодов мало, а десериализация дорогая


class Period(object):
    ''' Период. Задается началом и типом периода. Конец вычисляется, и не включен
    в период, т.е это полуинтервал [start; end).

    Возможные типы:

    :period_year: год, начинается 1 января, заканчивается 1 января след. года
    :period_halfyear: полугодие, начинается 01.01 или 01.07
    :period_quarter: квартал, начинается 01.01,  01.04, 01.07 или 01.10.
    :period_3quarters: 3 квартала, начинаются в один из кварталов
    :period_month: месяц, начинается 1 числа месяца
    :period_decade: декада, каждый месяц состоит из трех декад,
    начинается 1, 11, или 21 числа месяца
    :period_week: неделя, 7 дней, начинается в любой день
    :period_day: день, начинается и заканчивается в 00:00

    Не изменяемый (т.е. не надо менять _start и _period_type после ининциализации)
    TODO i18n
    '''
    quarter_months = [1, 4, 7, 10] # месяцы начала кварталов
    human_date_format = '%d.%m.%Y' # формат вывода даты
    week_postfix = u' (неделя)' # формат недели (что идет после даты начала)
    # внутренний формат хранения
    datetime_format = '%Y-%m-%d %H:%M:%S'
    datetime_format_fallback = '%Y-%m-%d'
    separator = '|'

    _month_names = {}
    _month_genitives = {}

    __slots__ = ["start", "end", "period_type", "_sort_key"]

    def __new__(typ, value):
        ''' :value:
        или tuple (start, period_type),
        или строка с сериализованным периодом
        или период
        '''
        if isinstance(value, str):
            period = _period_string_cache.get(value)
            if period is not None:
                return period
            else:
                try: start, period_type_id = value.split(Period.separator)
                except ValueError: start, period_type_id = value, period_day
                try:
                    start = tzutils.dt(datetime.strptime(start,
                        Period.datetime_format))
                except ValueError:
                    #  will still raise if wrong format
                    try: start = tzutils.dt(datetime.strptime(start,
                        Period.datetime_format_fallback))
                    except ValueError: # last resort
                        start = dt_from_iso(start)
                period_type = Obj(int(period_type_id))
        elif isinstance(value, Period):
            return value
        elif isinstance(value, tuple):
            start, period_type = value
            if not isinstance(start,date):
                raise TypeError(_('Неверная дата начала периода: ') +
                                str(start))
            if period_type not in PERIOD_TYPES:
                raise TypeError(_('Неверный тип периода: ') + str(period_type))
        else:
            raise TypeError(_('Невозможно создать период из %r') % value)
        start = Period.normalize_dict[period_type](Period, start)
        cache_key = (start, period_type)
        period = _period_cache.get(cache_key)
        if period is not None:
            return period
        period = object.__new__(typ)
        period.start = start
        period.period_type = period_type
        period.end = PERIOD_END_GETTERS[period_type](period)
        period._sort_key = (start, -int(period_type))
        _period_cache[cache_key] = period
        _period_string_cache[Period.serialize(period)] = period
        return period

    def __lt__(self, other):
        try:
            return self._sort_key < other._sort_key
        except AttributeError:
            return False

    # @total_ordering is not used for performance optimization - calling
    # __ne__ without lambda
    def __le__(self, other):
        try:
            return self._sort_key <= other._sort_key
        except AttributeError:
            return False

    def __gt__(self, other):
        try:
            return self._sort_key > other._sort_key
        except AttributeError:
            return False

    def __ge__(self, other):
        try:
            return self._sort_key >= other._sort_key
        except AttributeError:
            return False

    def __add__(self, other):
        try:
            shift = int(other)
        except (TypeError, ValueError):
            return NotImplemented
        else:
            return self.shift_period(shift)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        try:
            shift = -int(other)
        except ValueError :
            return NotImplemented
        except TypeError :
            if not isinstance(other, Period):
                return NotImplemented
            if other.period_type != self.period_type:
                return self.__sub__(Period((other.start, self.period_type)))
            return PERIOD_DIST[self.period_type] ( other , self )
        else:
            return self.shift_period(shift)

    def __rsub__(self, other):
        return self.__sub__(other)

    @classmethod
    def month_names(cls):
        ''' Названия месяцев
        '''
        lang = get_language()
        try:
            return cls._month_names[lang]
        except KeyError:
            _month_names = _(u'январь февраль март апрель май июнь '
                             u'июль август сентябрь октябрь '
                             u'ноябрь декабрь').split()
            assert len(_month_names) == 12
            cls._month_names[lang] = _month_names
            return _month_names

    @classmethod
    def month_genitives(cls):
        ''' Названия месяцев в родительном падеже
        '''
        lang = get_language()
        try:
            return cls._month_genitives[lang]
        except KeyError:
            _month_genitives = _(u'января февраля марта апреля мая '
                                 u'июня июля августа сентября октября '
                                 u'ноября декабря').split()
            assert len(_month_genitives) == 12
            cls._month_genitives[lang] = _month_genitives
            return _month_genitives

    @classmethod
    def make_quarter(cls, year, n_quarter):
        ''' Создать период - :n_quarter: квартал :year: года
        '''
        return cls((tzutils.dt(
                        datetime(year, cls.quarter_months[n_quarter - 1], 1)),
                    period_quarter))

    @classmethod
    def make_decade(cls, year, month, n_decade):
        ''' Создать период - :n_decade: декаду :month: месяца :year: года
        '''
        p = cls((tzutils.dt(datetime(year, month, 1)), period_decade))
        for __ in range(n_decade - 1):
            p = p.next_period()
        return p

    def __repr__(self):
        return '<Period %s %s>' % (self.start.strftime('%Y.%m.%d'),
                period_name_by_code[self.period_type])

    def __str__(self):
        return self.to_string()

    @classmethod
    def sort_key(cls, period):
        ''' Ключ для сортировки периодов так, чтобы они шли в хронологическом порядке
        '''
        return period._sort_key

    @classmethod
    def min(cls, *periods):
        return cls.sorted_list(periods)[0]

    @classmethod
    def max(cls, *periods):
        return cls.sorted_list(periods)[-1]

    @classmethod
    def sorted_list(cls, periods):
        periods = list(periods)
        periods.sort(key=cls.sort_key)
        return periods

    def __contains__ ( self , period ):
        ''' Возвращает истиность вхождения :period: в self как подмножества
        '''
        return isinstance(period, Period) \
            and self.start <= period.start and period.end <= self.end

    def serialize(self):
        try:
            strf = self.start.strftime(self.datetime_format)
        except ValueError:
            ##raise Exception('Incorrect start datetime: %s' % self.start)
            logging.error('Incorrect start datetime: %s' % self.start)
            strf = str(self.start) #'1900-01-01 00:00:00'
        return self.separator.join([strf, str(self.period_type)])

    @classmethod
    def deserialize(cls, value):
        ''' Может вернуть Period или RelativePeriod
        '''
        if re.match('^-?\d+\\' + cls.separator + '-?\d+$', value):
            return RelativePeriod.deserialize(value)
        return Period(value)

    # Параметры агрегации типов периодов
    # Тут указаны только непосредственные дети, полный список формируется рекурсивно.
    # Используется при составлении запросов при агрегации по периодам,
    # и для проверки вложенности типов периодов
    AGGR_CHILD_TYPES = {
        period_week: [period_day],
        period_decade: [period_day],
        period_month: [period_decade] + ( [period_week]
                                          if WEEK_AS_MONTHS_CHILD else [] ),
        period_quarter: [period_month],
        period_halfyear: [period_quarter],
        period_3quarters: [period_quarter],
        period_year: [period_halfyear],
        }

    def parents(self):
        ''' Все непосредственные родители данного периода -
        используется в агрегации
        '''
        return {
            period_day: lambda : [Period((self.start, period_decade)),
                                  Period((self.start, period_week))],
            period_week: lambda : ( [Period(self.start,period_month)]
                                    if WEEK_AS_MONTHS_CHILD else [] ),
            period_decade: lambda : [Period((self.start, period_month))],
            period_month: lambda : [Period((self.start, period_quarter))],
            period_quarter: lambda : [
                Period((self.start, period_halfyear)),
                Period((self.start, period_3quarters)),
                Period((self.prev_period().start, period_3quarters)),
                Period((self.prev_period().prev_period().start, period_3quarters)),
                ],
            period_halfyear: lambda : [Period((self.start, period_year))],
            period_3quarters: lambda : [],
            period_year: lambda : [],
            }[self.period_type]()

    def get_all_parents(self):
        p_set = set(self.parents())
        for p in list(p_set):
            p_set.update(p.get_all_parents())
        return p_set

    normalize_dict = {
        period_day: lambda cls, s: tzutils.dt(datetime(s.year, s.month, s.day)),
        period_week: lambda cls, s: tzutils.dt(datetime(s.year, s.month, s.day)),
        # неделя может начинаться с любого дня
        # - timedelta(days = s.weekday()),
        period_decade: lambda cls, s: tzutils.dt(datetime(
            s.year, s.month, 1 if s.day in range(1,11) else 11 \
                                if s.day in range(11,21) else 21)),
            #(s.day - 1) / 10 * 10 + 1),
        period_month: lambda cls, s: tzutils.dt(datetime(s.year, s.month, 1)),
        period_quarter: lambda cls, s: cls._normalize_quarter(s),
        period_halfyear: lambda cls, s: tzutils.dt(datetime(s.year, 1 if s.month < 7 else 7, 1)),
        period_3quarters: lambda cls, s: cls._normalize_quarter(s),
        period_year: lambda cls, s: tzutils.dt(datetime(s.year, 1, 1)),
        }

    @classmethod
    def _normalize_quarter(cls, s):
        for quarter_start in reversed(cls.quarter_months):
            if s.month >= quarter_start:
                return tzutils.dt(datetime(s.year, quarter_start, 1))

    def to_string(self):
        return self.to_html().replace('&nbsp;', ' ')

    def to_html(self):
        n_quarter = lambda s: self.quarter_months.index(s.month) + 1
        if self.period_type == period_3quarters:
            s = Period((self.start, period_quarter))
            e = s.next_period().next_period()
            return s.to_html() + ' - ' + e.to_html()
        return {
            period_day: lambda : self.start.strftime(self.human_date_format),
            period_week: lambda : _(u'с&nbsp;{start} по&nbsp;{end}').format(
                start=self.start.strftime(self.human_date_format),
                end=self.end.strftime(self.human_date_format)),
            period_decade : lambda : _(
                u'{n}&nbsp;декада {month} {year}&nbsp;г.').format(
                    n=(self.start.day - 1) // 10 + 1,
                    month=self.month_genitives()[self.start.month-1],
                    year=self.start.year),
            period_month: lambda : _(u'{month} {year}&nbsp;г.').format(
                month=self.month_names()[self.start.month - 1],
                year=self.start.year),
            period_quarter: lambda : _(u'{n}&nbsp;кв. {year}&nbsp;г.').format(
                n=n_quarter(self.start),
                year=self.start.year),
            period_halfyear: lambda : _(u'{n}&nbsp;п. {year}&nbsp;г.').format(
                n=1 if self.start.month < 7 else 2,
                year=self.start.year),
            period_year: lambda : _(u'{year}&nbsp;г.').format(
                year=self.start.year),
            }[self.period_type]()

    class Invalid(Exception): pass

    @classmethod
    def from_string(cls, value, extra_parse_date_fn=None):
        ''' Возвращает Period по to_string
        '''
        # см. также netdb.periods.js в netdb_slickgrid
        for period_type, regexp in [
            (period_year, _(r'''^
                            (?P<year>[1-9]\d{,3})       #year group
                            \s?г?\.?\s*                  #year abbr
                            $''')),
            (period_3quarters, _(r'''^
                                 (?P<quarter1>[1-4])     #first quarter group
                                 \s?кв\.?\s*             #quarter abbr
                                 (?P<year1>[1-9]\d{,3}) #first year group
                                 \s?г?\.?\s*             #year abbr
                                 -\s*
                                 (?P<quarter2>[1-4])     #second quarter group
                                 \s?кв\.?\s*             #quarter abbr
                                 (?P<year2>[1-9]\d{,3}) #second year group
                                 \s?г?\.?\s*             #year abbr
                                 $''')),
            (period_halfyear, _(r'''^
                                (?P<half>[1-2])          #half group
                                \s?п\.?\s*               #half abbr
                                (?P<year>[1-9]\d{,3})   #year group
                                \s?г?\.?\s*              #year abbr
                                $''')),
            (period_quarter, _(r'''^
                               (?P<quarter>[1-4])        #quarter group
                               \s?кв\.?\s*               #quarter abbr
                               (?P<year>[1-9]\d{,3})    #year group
                               \s?г?\.?\s*               #year abbr
                               $''')),
            (period_month, _(r'''^
                             (?P<month>[а-я]+)           #month group
                             \s*
                             (?P<year>[1-9]\d{,3})      #year group
                             \s?г?\.?\s*                 #year abbr
                             $''')),
            (period_decade, _(r'''^
                              (?P<decade>[1-3])          #decade group
                              \s?декада\s*               #decade abbr
                              (?P<month>[а-я]+)          #month group
                              \s*
                              (?P<year>[1-9]\d{,3})     #year group
                              \s?г?\.?\s*                #year abbr
                              $''')),
            (period_week, _(r'''^
                            с\s
                            (?P<week_start>\d{1,2}.\d{1,2}.\d{4}) #week start group
                            \sпо\s
                            (?P<week_end>\d{1,2}.\d{1,2}.\d{4})   #week end group
                            $''')),
            ]:
            match = re.match(regexp, value, re.X | re.I | re.U)
            if match:
                if period_type == period_year:
                    year = match.group('year')
                    start = tzutils.dt(
                            datetime(cls._check_year(int(year)), 1, 1))
                elif period_type == period_quarter:
                    group = match.group('quarter', 'year')
                    start = cls._quarters_from_string(period_type, group)
                elif period_type == period_3quarters:
                    group = match.group('quarter1', 'year1',
                                        'quarter2', 'year2')
                    start = cls._quarters_from_string(period_type, group)
                elif period_type == period_halfyear:
                    half, year = map(int, match.group('half', 'year'))
                    start = tzutils.dt(
                            datetime(cls._check_year(year),
                                     {1: 1, 2: 7}[half], 1))
                elif period_type == period_month:
                    month, year = match.group('month', 'year')
                    start = tzutils.dt(
                            datetime(cls._check_year(year),
                                     cls._check_month(month.lower()), 1))
                elif period_type == period_decade:
                    decade, month, year = match.group('decade', 'month', 'year')
                    decade = int(decade)
                    month = month.lower()
                    start = tzutils.dt(datetime(cls._check_year(year),
                                                cls._check_month(month),
                                                [1, 11, 21][decade - 1]))
                elif period_type == period_week:
                    start = tzutils.dt(
                        datetime.strptime(match.group('week_start'),
                                          cls.human_date_format))
                return Period((start, period_type))
        # try to parse period day
        period_type = period_day
        start = None
        try:
            start = tzutils.dt(datetime.strptime(value, cls.human_date_format))
        except ValueError:
            if extra_parse_date_fn:
                try:
                    start = extra_parse_date_fn(value)
                except ValueError:
                    pass
        if start:
            return Period((start, period_type))
        raise cls.Invalid(_('Значение не может быть приведено к периоду, '
                            'неизвестен формат данных.'))

    def to_default_start(self):
        ''' Возвращаем период, сдвинутый к "умолчательному" началу
        (сейчас актуально только для недели)
        '''
        if self.period_type == period_week:
            # сдвигаем начало недели к понедельнику
            return Period((self.start - timedelta(days=self.start.weekday()),
                self.period_type))
        else:
            return self

    @classmethod
    def _check_year(cls, year):
        ''' Проверяем, что год допустимый, и возвращаем его как целое
        '''
        min_year, max_year = tzutils.MIN.year, tzutils.MAX.year
        try: year = int(year)
        except ValueError:
            raise cls.Invalid(_(u'Введите год в числовом формате, '
                              u'например 2011, а не "%s"') % year)
        if not (min_year <= year <= max_year):
            raise cls.Invalid(
                _(u'Введите год от {0:d} до {1:d}, не "{2:d}".').format(
                    min_year, max_year, year))
        return year

    @classmethod
    def _check_month(cls, month):
        ''' Проверяем, что название месяца правильное, и возвращаем номер месяца
        '''
        if month in cls.month_names():
            return cls.month_names().index(month) + 1
        elif month in cls.month_genitives():
            return cls.month_genitives().index(month) + 1
        else:
            raise cls.Invalid(
                _(u'Введите правильное название месяца '
                  u'(одно из {0}), а не "{1}".')\
                .format(', '.join(cls.month_names()), month))

    @classmethod
    def _quarters_from_string(cls, period_type, match_groups):
        ''' Начало периода типа кваратал или 3 квартала по строке
        '''
        quarter, year = [int(val) for val in match_groups][:2]
        cls._check_year(year)
        if period_type == period_3quarters:
            q2, y2 = [int(val) for val in match_groups][2:]
            cls._check_year(y2)
        start = tzutils.dt(
                datetime(cls._check_year(year), cls.quarter_months[quarter - 1], 1))
        if period_type == period_3quarters:
            exp_end = cls._shift_quarter(start, 2).start
            end = tzutils.dt(
                    datetime(cls._check_year(y2), cls.quarter_months[q2 - 1], 1))
            if end != exp_end:
                raise cls.Invalid(
                    _(u'Длина периода не 3 квартала: ожидаемый конец "{0}", а не "{1}"').format(
                        Period((exp_end, period_quarter)),
                        Period((end, period_quarter))))
        return start

    @classmethod
    def _all_child_types(cls, parent_type):
        ''' Все дети периода при агрегации
        '''
        for t in cls.AGGR_CHILD_TYPES.get(parent_type, []):
            yield t
            for t_ in cls._all_child_types(t):
                yield t_

    @classmethod
    def period_type_lte(cls, pt1, pt2):
        ''' Тип периода pt1 вложен в тип периода pt2 (или они совпадают)
        '''
        return pt1 == pt2 or (pt1 in cls._all_child_types(pt2))

    def in_subtree(self, high_period):
        ''' Находится ли данный период в поддереве high_period?
        '''
        return (Period.period_type_lte(
            self.period_type, high_period.period_type) and
                self.start >= high_period.start and
                self.start < high_period.end)

    def get_children(self, max_depth=None):
        ''' Вернуть список непосредственных детей
        :max_depth: указывает на самых мелких детей, которые будут показаны
        max_depth=period_month -- годы, кваралы и месяцы, без дней
        max_depth=period_quarter -- видны годы и кварталы без месяцев
        и т.п.
        '''
        s = self.start
        if max_depth is not None and \
               PERIOD_TYPES.index(max_depth) >= PERIOD_TYPES.index(self.period_type):
            return []
        return {
            period_year: lambda : [
                Period((tzutils.dt(datetime(s.year, m, 1)), period_halfyear))
                for m in [1, 7]],
            period_3quarters: lambda : [
                self._shift_quarter(s, shift) for shift in range(3)],
            period_halfyear: lambda : [
                Period((tzutils.dt(datetime(s.year, m, 1)), period_quarter))
                for m in ([1, 4] if s.month == 1 else [7, 10])],
            period_quarter: lambda : [
                Period((tzutils.dt(datetime(s.year, m, 1)), period_month))
                for m in {
                    1: (1, 2, 3), 4: (4, 5, 6),
                    7: (7, 8, 9), 10: (10, 11, 12)}[s.month]],
            period_month: lambda : [
                Period((tzutils.dt(datetime(s.year, s.month, d)),
                        period_decade))
                                    for d in (1, 11, 21)]+( [
                # все недели, начинающиеся тут:
                Period((s+timedelta(i),period_week))
                for i in range(31)
                if s+timedelta(i) < self.end ]
                if WEEK_AS_MONTHS_CHILD else [] ),
            period_decade: lambda : [
                # третья декада может быть 11 дней длиной, поэтому xrange(11)
                Period((s + timedelta(days=i), period_day)) for i in range(11)\
                        # Тут проверяется, что мы не вышли за пределы месяца
                                if s + timedelta(days=i)  < self.end],
            period_week: lambda : [
                Period((s + timedelta(days=i), period_day)) for i in range(7)],
            period_day: lambda : []}[self.period_type]()

    def get_all_children(self):
        ''' Вернуть всех детей, детей детей и т.д. Итератор.
        '''
        for ch in self.get_children():
            yield ch
            for c in ch.get_all_children():
                yield c

    def get_days(self):
        '''Вернуть список дней в периоде'''
        s = self.start
        days = (self.end - s).days
        return [Period((s + timedelta(days=i), period_day)) for i in range(days)]

    @classmethod
    def _shift_quarter(cls, start, shift):
        p = Period((start, period_quarter))
        for __ in range(abs(shift)):
            p = p.next_period() if shift > 0 else p.prev_period()
        return p

    def next_period(self, small_step=False):
        ''' Следующий период
        '''
        if self.period_type == period_3quarters:
            return Period((self._shift_quarter(self.start, 1).start,
                           period_3quarters))
        elif self.period_type == period_week:
            s = 1 if small_step else 7
            return Period((self.start + timedelta(days=s), self.period_type))
        else:
            return Period((self.end + timedelta(seconds=1), self.period_type))

    def prev_period(self, small_step=False):
        ''' Предыдущий период
        '''
        if self.period_type == period_3quarters:
            return Period((self._shift_quarter(self.start, -1).start,
                           period_3quarters))
        elif self.period_type == period_week:
            s = 1 if small_step else 7
            return Period((self.start - timedelta(days=s), self.period_type))
        else:
            return Period((self.start - timedelta(seconds=1), self.period_type))

    def lte_this_year(self, reverse=False):
        ''' Список периодов <= данного в том же году
        :reverse: если True, значит >= данного в том же году (gte_this_year)
        '''
        p_list = [self]
        while True:
            last = p_list[-1]
            p = last.next_period() if reverse else last.prev_period()
            if p.start.year == self.start.year:
                p_list.append(p)
            else:
                return p_list

    def gte_this_year(self):
        ''' Список периодов >= данного в том же году
        '''
        return self.lte_this_year(reverse=True)

    def shift_period(self, shift):
        ''' Сдвинуть себя на shift (вернуть новый период)
        '''
        p = self
        for __ in range(abs(shift)):
            p = p.next_period() if shift > 0 else p.prev_period()
        return p

    @classmethod
    def period_types_by_names(cls):
        return period_code_by_name

class RelativePeriod(object):

    def __init__(self, *args):
        ''' Сдвиг по определенному типу периода на offset единиц.
        Создание при помощи
        RelativePeriod(offset, period_type), или
        RelativePeriod(relative_period), или
        RelativePeriod(serialized_string_value)
        '''
        if len(args) == 2:
            self.offset, self.period_type = args
        elif len(args) == 1:
            value = args[0]
            if isinstance(value, RelativePeriod):
                self.offset, self.period_type = value.offset, value.period_type
            elif isinstance(value, str):
                offset, period_type_id = value.split(Period.separator)
                self.offset, self.period_type = int(offset), Obj(int(period_type_id))
            else:
                raise TypeError('Can not create RelativePeriod from args %r' % args)
        else:
            raise TypeError('__init__ takes one or two arguments')

    def __hash__(self):
        return hash((self.offset, self.period_type))

    def __eq__(self, other):
        return (isinstance(other, RelativePeriod) and self.offset ==
                other.offset and self.period_type == other.period_type)

    @property
    def _sort_key(self): return self.period_type, self.offset

    def __lt__(self, other):
        try:
            return self._sort_key < other._sort_key
        except AttributeError:
            return False

    def __le__(self, other):
        try:
            return self._sort_key <= other._sort_key
        except AttributeError:
            return False

    def __gt__(self, other):
        try:
            return self._sort_key > other._sort_key
        except AttributeError:
            return False

    def __ge__(self, other):
        try:
            return self._sort_key >= other._sort_key
        except AttributeError:
            return False

    def get_period(self, period):
        ''' Конкретный период относительно базового, или None,
        если тип базового периода более крупный, чем тип данного периода
        '''
        if not Period.period_type_lte(period.period_type, self.period_type):
            # т.е. можно создать месяц по дню, но нельзя день по месяцу
            return None
        else:
            return self.get_period_from_start(period.start)

    def get_period_from_rel_p_type(self, relative_period_type, now=None):
        ''' Период по типу базвого периода (должен быть больше чем :self:).
        Считаем относительно now, по умолчанию - текущий момент времени.
        '''
        if not Period.period_type_lte(self.period_type, relative_period_type):
            return None
        now = now or retrospection.now()
        return self.get_period_from_start(
                Period((now, relative_period_type)).to_default_start().start,
                small_step=True)

    @classmethod
    def get_rel_period_from_period_rel_p_type(cls,
            period, relative_period_type, now=None):
        ''' Обратная к get_period_from_rel_p_type функция - возвращает
        относительный период исходя из периода и типа относительного периода.
        То есть вычисляет сдвиг :period: относительно
        Period((relative_period_type, now))
        '''
        if not Period.period_type_lte(period.period_type, relative_period_type):
            return None
        now = now or retrospection.now()
        base_period = Period((now, relative_period_type)).to_default_start()
        start_period = Period((base_period.start, period.period_type))
        shift = 0
        if start_period.start < period.start:
            while start_period.start < period.start:
                start_period = start_period.next_period(small_step=True)
                shift += 1
        elif start_period.start > period.start:
            while start_period.start > period.start:
                start_period = start_period.prev_period(small_step=True)
                shift -= 1
        assert start_period == period
        return cls(shift, period.period_type)

    def get_period_from_start(self, now, small_step=False):
        ''' Конкретный период относительно момента вермени now
        '''
        return self.shift_period(Period((now, self.period_type)),
                small_step=small_step)

    def shift_period(self, period, reverse=False, small_step=False):
        ''' Сдвинуть данный period на offset.
        :reverse: = True - в противоположную сторону
        '''
        p = period
        for __ in range(abs(self.offset)):
            if (not reverse and self.offset > 0) or (reverse and self.offset < 0):
                p = p.next_period(small_step=small_step)
            else:
                p = p.prev_period(small_step=small_step)
        return p

    def serialize(self):
        return Period.separator.join(map(str, [self.offset, self.period_type.id]))

    @classmethod
    def deserialize(cls, value):
        offset, period_type_id = value.split(Period.separator)
        return cls(int(offset), Obj(int(period_type_id)))

    def to_string(self):
        title = _(u'Текущий ') + period_name_by_code[self.period_type].lower()
        return (title + ' ' + str(self.offset)) if self.offset else title

    def __repr__(self):
        return '<RelativePeriod %r %r>' % (self.offset, self.period_type)


def get_number_of_days(date, period_type):
    if isinstance(date, Period):
        date = date.start
    period = Period((date, period_type))
    return (period.end - period.start).days


#deprecated
def get_number_days_in_quarter(date):
    return get_number_of_days(date, period_quarter)


def get_number_days_from_start_quarter(date):
    if isinstance(date, Period):
        date = date.start
    period =  Period((date, period_quarter))
    return (date - period.start).days


def to_workday(period):
    ''' Приведение к периоду того же типа с началом в ближайший рабочий день
    в будущем
    '''
    return to_workday_sig(period, +1)


def to_workday_before(period):
    ''' Приведение к периоду того же типа с началом в ближайший рабочий день
    в прошлом
    '''
    return to_workday_sig(period, -1)


_to_workday_sig_cache = {}

def to_workday_sig(period, sig):
    key = (period, sig)
    res = _to_workday_sig_cache.get(key)
    if res is None:
        start = period.start
        while start.weekday() in (5, 6): # сб, вс
            start += timedelta(days=sig)
        res = _to_workday_sig_cache[key] = Period((start, period.period_type))
    return res


def get_prev_periods_gte_type_start(period, p_type, prev_period_getter=
        lambda period: period.prev_period):
    first_p_start = Period((Period((period.start, p_type)).start,
        period.period_type)).start
    period = prev_period_getter(period)
    while period.start >= first_p_start:
        yield period
        period = prev_period_getter(period)


def get_next_periods_lt_type_start(period, p_type, next_period_getter=
        lambda period: period.next_period):
    last_p_start = Period((next_period_getter(Period((period.start,
        p_type))).start, period.period_type)).start
    period = next_period_getter(period)
    while period.start < last_p_start:
        yield period
        period = next_period_getter(period)


# pickle support

def period_pickler(period):
    return period_unpickler, (period.serialize(),)

def period_unpickler(data):
    return Period.deserialize(data)

copyreg.pickle(Period, period_pickler, period_unpickler)
