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


class project_manager(models.Model):
    _name = 'project_budget.project_manager'
    _description = "project_manager"
    name = fields.Char(string="project_manager name", required=True)
    code = fields.Char(string="project_manager code", required=True)
    descr = fields.Char(string="project_manager description")
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

    @ api.depends("manager_rule.project_manager_access_ids.project_manager_id","manager_rule.project_manager_access_ids.user_id")
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
    code = fields.Char(string="customer_organization code", required=True)
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


