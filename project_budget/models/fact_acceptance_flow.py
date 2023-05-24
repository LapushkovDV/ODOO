from odoo import _, models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools import pytz
from datetime import timedelta

class fact_acceptance_flow(models.Model):

    def get_project_steps_list(self):
        domain = [('id', '=', 0)]
        project_steps = self.env['project_budget.project_steps'].search([('projects_id.id', '=', self.env.projects_id.id)])
        project_steps_list = []
        for each in project_steps:
            project_steps_list.append(each.id)
        if project_steps_list:
            domain = [('id', 'in', project_steps_list)]
            return domain
        return domain

    _name = 'project_budget.fact_acceptance_flow'
    _description = "fact acceptance flow"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    projects_id = fields.Many2one('project_budget.projects', string='projects_id', index=True,ondelete='cascade')
    project_have_steps = fields.Boolean(string="project have steps", related='projects_id.project_have_steps',
                                        readonly=True)
    project_steps_id = fields.Many2one('project_budget.project_steps', string='project_steps_id', index=True,ondelete='cascade')
    date_cash = fields.Date(string="date_cash" , required=True, copy=True)
    currency_id = fields.Many2one('res.currency', string='Account Currency', compute='_compute_reference')
    sum_cash_without_vat = fields.Monetary(string="sum_cash_without_vat", required=True, copy=True)
    sum_cash = fields.Monetary(string="sum_cash", required=True, copy=True, compute='_compute_sum')

    doc_cash = fields.Char(string="doc_cash", copy=True) #20230403 Вавилова Ирина сказла убрать из формы...
    @ api.depends('projects_id.currency_id')
    def _compute_reference(self):
        for row in self:
            row.currency_id = row.projects_id.currency_id
    @api.depends("sum_cash_without_vat","project_steps_id.vat_attribute_id","projects_id.vat_attribute_id")
    def _compute_sum(self):
        for row in self:
            if row.project_steps_id:
                row.sum_cash = row.sum_cash_without_vat * (1+row.project_steps_id.vat_attribute_id.percent / 100)
            else:
                row.sum_cash = row.sum_cash_without_vat * (1 + row.projects_id.vat_attribute_id.percent / 100)
