from ast import literal_eval
from odoo import models, fields, api

# catalogs
class project_office(models.Model):
    _name = 'project_budget.project_office'
    _description = "project_office"
    name = fields.Char(string="project_office name", required=True)
    code = fields.Char(string="project_office code", required=True)
    descr = fields.Char(string="project_office description")

class project_supervisor(models.Model):
    _name = 'project_budget.project_supervisor'
    _description = "project_supervisor"
    name = fields.Char(string="project_supervisor name", required=True)
    code = fields.Char(string="project_supervisor code", required=True)
    descr = fields.Char(string="project_supervisor description")
    user_id = fields.Many2one('res.users', string='user id',  required=True,)
    avatar_128 = fields.Image(related='user_id.avatar_128', readonly=True)
    project_supervisor_access_ids = fields.One2many(
            comodel_name='project_budget.project_supervisor_access',
            inverse_name='project_supervisor_id',
            string="project_manager_access",
            copy=True, auto_join=True)

class project_supervisor_access(models.Model):
    _name = 'project_budget.project_supervisor_access'
    _description = "project_supervisor_access"
    project_supervisor_id = fields.Many2one('project_budget.project_supervisor', string='project supervisor id',  required=True,)
    user_id = fields.Many2one('res.users', string='user id',  required=True,)
    can_approve_project = fields.Boolean(string="Can approve project as supervisor", default = False)
    descr = fields.Char(string="project supervisor access description")
    user_id = fields.Many2one('res.users', string='user id', required=True,)

class project_manager(models.Model):
    _name = 'project_budget.project_manager'
    _description = "project_manager"
    name = fields.Char(string="project_manager name", required=True)
    code = fields.Char(string="project_manager code", required=True)
    descr = fields.Char(string="project_manager description")
    user_id = fields.Many2one('res.users', string='user id', required=True,)
    avatar_128 = fields.Image(related='user_id.avatar_128', readonly=True)
    project_manager_access_ids = fields.One2many(
        comodel_name='project_budget.project_manager_access',
        inverse_name='project_manager_id',
        string="project_manager_access",
        copy=True, auto_join=True)

class project_manager_access(models.Model):
    _name = 'project_budget.project_manager_access'
    _description = "project_manager access"
    project_manager_id = fields.Many2one('project_budget.project_manager', string='project manager id', required=True,)
    user_id = fields.Many2one('res.users', string='user id', required=True,)
    descr = fields.Char(string="project manager access description")

class users_budgets_access(models.Model):
    _inherit = 'res.users'
    # _name = "users_budgets_access"
    _description = "users budgets access"
    project_manager_access_ids = fields.One2many(
        comodel_name='project_budget.project_manager_access',
        inverse_name='user_id',
        string="project_manager_access",
        copy=False, auto_join=True)
    project_supervisor_access_ids = fields.One2many(
        comodel_name='project_budget.project_supervisor_access',
        inverse_name='user_id',
        string="project_supervisor_access",
        copy=False, auto_join=True)

    supervisor_rule = fields.Many2many(compute='_get_list_supervisor_access_ids', comodel_name='project_budget.project_supervisor')
    manager_rule = fields.Many2many(compute='_get_list_manager_access_ids', comodel_name='project_budget.project_manager')

    @ api.depends("project_supervisor_access_ids.user_id","project_supervisor_access_ids.project_supervisor_id","project_supervisor_access_ids.descr")
    def _get_list_supervisor_access_ids(self):
        supervisor_access = self.env['project_budget.project_supervisor_access'].search([('user_id.id', '=', self.env.user.id)])
        supervisor_list = []
        if not supervisor_access :
            supervisors = self.env['project_budget.project_supervisor'].search([])
            for each in supervisors:
                supervisor_list.append(each.id)
        else :
            for each in supervisor_access:
                supervisor_list.append(each.project_supervisor_id.id)
        for rec in self:
            rec.supervisor_rule = supervisor_list

    @ api.depends("project_manager_access_ids.project_manager_id","project_manager_access_ids.user_id")
    def _get_list_manager_access_ids(self):
        manager_access = self.env['project_budget.project_manager_access'].search([('user_id.id', '=', self.env.user.id)])
        manager_list = []
        if not manager_access :
            managers = self.env['project_budget.project_manager'].search([])
            for each in managers:
                manager_list.append(each.id)
        else :
            for each in manager_access:
                manager_list.append(each.project_manager_id.id)
        for rec in self:
            rec.manager_rule = manager_list



class customer_organization(models.Model):
    _name = 'project_budget.customer_organization'
    _description = "project_customer organization"
    name = fields.Char(string="customer_organization name", required=True)
    longname = fields.Char(string="customer_organization long name", )
    code = fields.Char(string="customer_organization code", )
    inn = fields.Char(related='partner_id.vat', readonly=True)
    avatar_128 = fields.Image(related='partner_id.avatar_128', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', copy=True, domain="[('is_company','=',True)]")
    descr = fields.Char(string="customer_organization description")

class customer_status(models.Model):
    _name = 'project_budget.customer_status'
    _description = "project_castomer status"
    name = fields.Char(string="customer_status name", required=True)
    code = fields.Char(string="customer_status code", required=True)
    descr = fields.Char(string="customer_status description")

class industry(models.Model):
    _name = 'project_budget.industry'
    _description = "project_industry"
    name = fields.Char(string="industry name", required=True)
    code = fields.Char(string="industry code", required=True)
    descr = fields.Char(string="industry description")

class vat_attribute(models.Model):
    _name = 'project_budget.vat_attribute'
    _description = "project_vat attribute"
    name = fields.Char(string="vat_attribute name", required=True)
    code = fields.Char(string="vat_attribute code", required=True)
    percent = fields.Float(string="vat_percent", required=True, default=0)
    descr = fields.Char(string="vat_attribute description")

class legal_entity_signing(models.Model):
    _name = 'project_budget.legal_entity_signing'
    _description = "project_legal entity signing"
    name = fields.Char(string="legal_entity_signing name", required=True)
    code = fields.Char(string="legal_entity_signing code", required=True)
    percent_fot = fields.Float(string="fot_percent", required=True, default=0)
    descr = fields.Char(string="legal_entity_signing description")

class project_type(models.Model):
    _name = 'project_budget.project_type'
    _description = "project_type"
    name = fields.Char(string="project_type name", required=True)
    code = fields.Char(string="project_type code", required=True)
    descr = fields.Char(string="project_type description")

class technological_direction(models.Model):
    _name = 'project_budget.technological_direction'
    _description = "project_technologigal direction"
    name = fields.Char(string="technological_direction name", required=True)
    code = fields.Char(string="technological_direction code", required=True)
    descr = fields.Char(string="technological_direction description")


class estimated_probability(models.Model):
    _name = 'project_budget.estimated_probability'
    _description = "project_estimated_probability"
    _order = "code"
    name = fields.Char(string="estimated_probability name", required=True, )
    code = fields.Char(string="estimated_probability code", required=True, )
    color = fields.Integer('Color')
    # count_approve_state_manager = fields.Integer(compute='_compute_probability_count')
    # count_approve_state_supervisor = fields.Integer(compute='_compute_probability_count')
    # count_approve_state_approved = fields.Integer(compute='_compute_probability_count')
    count_approve_state_total = fields.Integer(compute='_compute_probability_count')
    # sum_revenue_approve_state_manager = fields.Integer(compute='_compute_probability_count')
    # sum_revenue_approve_state_supervisor = fields.Integer(compute='_compute_probability_count')
    # sum_revenue_approve_state_approved = fields.Integer(compute='_compute_probability_count')
    sum_revenue_approve_state_total = fields.Integer(compute='_compute_probability_count')
    sum_margin_income_total  = fields.Integer(compute='_compute_probability_count')
    sum_cost_price_total  = fields.Integer(compute='_compute_probability_count')
    def _compute_probability_count(self):
        domains = {
            # 'count_approve_state_manager' : [('approve_state', '=', 'need_approve_manager')],
            # 'count_approve_state_supervisor' : [('approve_state', '=', 'need_approve_supervisor')],
            # 'count_approve_state_approved' : [('approve_state', '=', 'approved')],
            'count_approve_state_total':[]
        }
        for field in domains:
            data = self.env['project_budget.projects']._read_group(domains[field]+
                [('budget_state','=','work'),('estimated_probability_id', 'in', self.ids)]
                ,['estimated_probability_id'], ['estimated_probability_id'])
            count = {
                x['estimated_probability_id'][0]: x['estimated_probability_id_count']
                for x in data if x['estimated_probability_id']
            }
            for record in self:
                record[field] = count.get(record.id, 0)

        domains = {
            # 'sum_revenue_approve_state_manager': [('approve_state', '=', 'need_approve_manager')],
            # 'sum_revenue_approve_state_supervisor': [('approve_state', '=', 'need_approve_supervisor')],
            # 'sum_revenue_approve_state_approved': [('approve_state', '=', 'approved')],
            'sum_revenue_approve_state_total': []
        }
        for field in domains:
            data = self.env['project_budget.projects']._read_group(domains[field]+
                [('budget_state','=','work'),('estimated_probability_id', 'in', self.ids)]
                ,['estimated_probability_id','sum_total:sum(total_amount_of_revenue)'], ['estimated_probability_id'])

            sum = {
                x['estimated_probability_id'][0]: x['sum_total']
                for x in data if x['estimated_probability_id']
            }
            for record in self:
                record[field] = sum.get(record.id, 0)

        domains = {
            # 'sum_revenue_approve_state_manager': [('approve_state', '=', 'need_approve_manager')],
            # 'sum_revenue_approve_state_supervisor': [('approve_state', '=', 'need_approve_supervisor')],
            # 'sum_revenue_approve_state_approved': [('approve_state', '=', 'approved')],
            'sum_margin_income_total': []
        }
        for field in domains:
            data = self.env['project_budget.projects']._read_group(domains[field]+
                [('budget_state','=','work'),('estimated_probability_id', 'in', self.ids)]
                ,['estimated_probability_id','sum_total:sum(margin_income)'], ['estimated_probability_id'])

            sum = {
                x['estimated_probability_id'][0]: x['sum_total']
                for x in data if x['estimated_probability_id']
            }
            for record in self:
                record[field] = sum.get(record.id, 0)

        domains = {
            # 'sum_revenue_approve_state_manager': [('approve_state', '=', 'need_approve_manager')],
            # 'sum_revenue_approve_state_supervisor': [('approve_state', '=', 'need_approve_supervisor')],
            # 'sum_revenue_approve_state_approved': [('approve_state', '=', 'approved')],
            'sum_cost_price_total': []
        }
        for field in domains:
            data = self.env['project_budget.projects']._read_group(domains[field] +
                [('budget_state', '=', 'work'), ('estimated_probability_id', 'in', self.ids)]
                , ['estimated_probability_id','sum_total:sum(cost_price)'],['estimated_probability_id'])
            sum = {
                x['estimated_probability_id'][0]: x['sum_total']
                for x in data if x['estimated_probability_id']
            }
            for record in self:
                record[field] = sum.get(record.id, 0)


    def _get_action(self, action_xmlid,context):
        action = self.env["ir.actions.actions"]._for_xml_id(action_xmlid)
        if self:
            action['display_name'] = self.display_name

        default_immediate_tranfer = True

        action_context = literal_eval(action['context'])
        context = {**action_context, **context}
        action['context'] = context
        return action

    def get_action_projects_0(self):
        context = {
            "estimated_probability_0": True
        }
        return self._get_action('project_budget.show_comercial_budget_spec',context)
    def get_action_projects_0(self):
        context = {"search_default_estimated_probability_0": True}
        return self._get_action('project_budget.show_comercial_budget_spec',context)
    def get_action_projects_30(self):
        context = {"search_default_estimated_probability_30": True}
        return self._get_action('project_budget.show_comercial_budget_spec',context)
    def get_action_projects_50(self):
        context = {"search_default_estimated_probability_50": True}
        return self._get_action('project_budget.show_comercial_budget_spec',context)
    def get_action_projects_75(self):
        context = {"search_default_estimated_probability_75": True}
        return self._get_action('project_budget.show_comercial_budget_spec',context)
    def get_action_projects_100(self):
        context = {"search_default_estimated_probability_100": True}
        return self._get_action('project_budget.show_comercial_budget_spec',context)

