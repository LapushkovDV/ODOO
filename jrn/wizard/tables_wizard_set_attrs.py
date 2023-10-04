from odoo import models, fields, _
from odoo.exceptions import UserError


list_table_names=[]

class tables_wizard_set_attrs(models.TransientModel):
    _name = 'jrn.wizard.set_table_attrs'
    _description = 'jrn wizard for set table attrs'
    # array_table_names  = fields.Selection(list_table_names, string='table names')
    check_changes = fields.Boolean(string='check changes', default = False)

    def get_fields_table_prefix(self, table):
        sql_string = "SELECT t1.column_name FROM information_schema.columns t1  WHERE t1.table_name = '{0}' ;"
        sql_string = sql_string.format(table.name)
        print('recreate table columns sql_string = ', sql_string)
        self.env.cr.execute(sql_string)

        select_fields_string = ''
        for record_jrn in self.env.cr.fetchall():
            if select_fields_string == '':
                select_fields_string += '{0}"'+''.join(record_jrn)+'"'
            else:
                select_fields_string += ',{0}"' + ''.join(record_jrn)+'"'
        return  select_fields_string

    def get_fields_table(self, table):
        str = self.get_fields_table_prefix(table)
        str = str.format(' ')
        return str



    def create_trigger(self, table):
        query_function = """DROP TRIGGER IF EXISTS "jrn_{0}" on "{0}" CASCADE ;
                            DROP FUNCTION IF EXISTS "{0}_tp"();
        """
        query_function = query_function.format(table.name)
        print('query_function = ', query_function)
        self.env.cr.execute(query_function)

        query_function =  """
            -- FUNCTION: "{0}_tp"()
            
            -- DROP FUNCTION "{0}_tp"();
                        
            CREATE FUNCTION "{0}_tp"()
                RETURNS trigger
                LANGUAGE 'plpgsql'
                COST 100
                VOLATILE NOT LEAKPROOF SECURITY DEFINER
            AS $BODY$
            DECLARE
             VTABLEID bigint;                          
             VOPERATION INTEGER;
             vid integer;
            BEGIN
            
               IF TG_OP = 'INSERT' THEN VOPERATION := 2; VTABLEID := NEW.id;
               ELSIF TG_OP = 'UPDATE' THEN VOPERATION := 4; VTABLEID := NEW.id;
               ELSE VOPERATION := 8; VTABLEID := OLD.id;
               END IF;

               INSERT INTO jrn_jrn (table_name_id, table_id, datetime_event, user_event, status, operation)
               VALUES({1}, VTABLEID, NOW(), '1', 0, VOPERATION) RETURNING id INTO vid;
            
               IF TG_OP = 'DELETE' OR TG_OP = 'UPDATE' THEN
                   INSERT INTO jrn_{0}(
                   jrn_id,jrn_oldnewrec,{2}) 
                    VALUES(
                    vid,2,{3}
                    );
               END IF;
               
               IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
                   INSERT INTO jrn_{0}(                   
                    jrn_id,jrn_oldnewrec,{2}
                    )
                    VALUES(
                     vid,1,{4}
                    );
             END IF;
            RETURN NULL; END;
            
            $BODY$;
            
            
            GRANT EXECUTE ON FUNCTION "{0}_tp"() TO PUBLIC;
        """
        # ALTER FUNCTION "{0}_tp"() OWNER TO postgres;
        # GRANT EXECUTE ON FUNCTION "{0}_tp"() O postgres;

        fields =self.get_fields_table(table)
        print('fields = ', fields)
        old_fields = self.get_fields_table_prefix(table).format('OLD.')
        print('old_fields = ', old_fields)
        new_fields = self.get_fields_table_prefix(table).format('NEW.')
        print('new_fields = ', new_fields)
        query_function = query_function.format(table.name, table.id, fields, old_fields, new_fields)
        self.env.cr.execute(query_function)
        print('query_function = ', query_function)

        query_trg = """
         
        
        CREATE TRIGGER "jrn_{0}" 
        AFTER INSERT OR DELETE OR UPDATE ON {0} 
        FOR EACH ROW EXECUTE PROCEDURE "{0}_tp"();"""
        query_trg = query_trg.format(table.name)
        print('query_trg = ', query_trg)
        self.env.cr.execute(query_trg)
        return ''

    def drop_trigger(self,table):
        return False

    def action_set_attrs(self):
        context_list = self.env.context
        if context_list.get('active_ids'):
            active_ids = context_list['active_ids']

        tables = self.env['jrn.tables'].search([('id', 'in', active_ids)])
        for table in tables:
            table.check_changes = self.check_changes
            if table.check_changes == True:
                self.create_trigger(table)
            else:
                self.drop_trigger(table)
        return None

