from odoo import _, models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools import pytz
from datetime import timedelta

class planned_cash_flow(models.Model):

    _name = 'project_budget.planned_cash_flow'
    _description = "planned cash flow"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    projects_id = fields.Many2one('project_budget.projects', string='projects_id',index=True,ondelete='cascade')
    etalon_budget = fields.Boolean(related='projects_id.etalon_budget', readonly=True)
    date_actual = fields.Datetime(related='projects_id.date_actual', readonly=True)

    project_have_steps = fields.Boolean(string="project have steps", related='projects_id.project_have_steps', readonly=True)
    project_steps_id = fields.Many2one('project_budget.project_steps', string='project_steps_id', index=True,ondelete='cascade')

    date_cash = fields.Date(string="date_cash" , required=True, copy=True)
    currency_id = fields.Many2one('res.currency', string='Account Currency', compute='_compute_reference')
    sum_cash_without_vat = fields.Monetary(string="sum_cash_without_vat", required=True, copy=True, compute='_compute_sum')
    sum_cash = fields.Monetary(string="sum_cash", required=True, copy=True)
    doc_cash = fields.Char(string="doc_cash",  copy=True) #20230403 Вавилова Ирина сказла убрать из формы...

    @ api.depends('projects_id.currency_id')
    def _compute_reference(self):
        for row in self:
            row.currency_id = row.projects_id.currency_id

    @api.depends("sum_cash","project_steps_id.vat_attribute_id","projects_id.vat_attribute_id")
    def _compute_sum(self):
        for row in self:
            if row.project_steps_id:
                row.sum_cash_without_vat = row.sum_cash/(1+row.project_steps_id.vat_attribute_id.percent / 100)
            else:
                row.sum_cash_without_vat = row.sum_cash / (1 + row.projects_id.vat_attribute_id.percent / 100)

