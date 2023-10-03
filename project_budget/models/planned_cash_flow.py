from odoo import _, models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools import pytz
from datetime import date

class planned_cash_flow(models.Model):

    _name = 'project_budget.planned_cash_flow'
    _description = "planned cash flow"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name_to_show'
    def compute_distribution_sum(self):
        for row in self:
            row.distribution_sum_with_vat = row.distribution_sum_without_vat = 0
            row.distribution_sum_with_vat_ostatok = row.distribution_sum_without_vat_ostatok =0
            for distribution_cash in row.distribution_cash_ids:
                row.distribution_sum_with_vat += distribution_cash.sum_cash
                row.distribution_sum_without_vat += distribution_cash.sum_cash_without_vat
            row.distribution_sum_with_vat_ostatok =row.sum_cash - row.distribution_sum_with_vat
            row.distribution_sum_without_vat_ostatok = row.sum_cash_without_vat - row.distribution_sum_without_vat

    cash_id = fields.Char(string="acceptance_id", required=True, copy=True, default='-'
                                # lambda self: self.env['ir.sequence'].sudo().next_by_code('project_budget.planned_acceptance_flow')
                                , index=True, readonly=True)
    name_to_show = fields.Char(string='name_to_show', compute='_get_name_to_show')
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
    budget_state = fields.Selection(related='projects_id.budget_state', readonly=True)
    approve_state = fields.Selection(related='projects_id.approve_state', readonly=True)

    distribution_cash_ids = fields.One2many(
        comodel_name='project_budget.distribution_cash',
        inverse_name='planned_cash_flow_id',
        string="distribution cash fact by plan", auto_join=True,copy=False)  # вот с копированием засада... вручную будем переносить ссылки прикопировании бюджета

    distribution_sum_with_vat = fields.Monetary(string="distribution sum with vat", compute='_compute_distribution_sum')
    distribution_sum_without_vat = fields.Monetary(string="distribution sum without vat", compute='_compute_distribution_sum')
    distribution_sum_without_vat_ostatok = fields.Monetary(string="distribution_sum_without_vat_ostatok", compute='_compute_distribution_sum')
    distribution_sum_with_vat_ostatok = fields.Monetary(string="distribution_sum_with_vat_ostatok", compute='_compute_distribution_sum')


    @api.depends('date_cash','project_steps_id')
    def _get_name_to_show(self):
        for prj in self:
            prj.name_to_show = prj.date_cash.strftime("%d/%m/%Y")
            if prj.project_have_steps == True:
                prj.name_to_show += _(' | step ') + (prj.project_steps_id.step_id or '') + '|'+ (prj.project_steps_id.code or '' )


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

    @api.depends("distribution_cash_ids","distribution_cash_ids.sum_cash")
    def _compute_distribution_sum(self):
        self.compute_distribution_sum()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('cash_id') or vals['cash_id'] == '-':
                vals['cash_id'] = self.env['ir.sequence'].sudo().next_by_code('project_budget.planned_cash_flow')
        return super().create(vals_list)

    def action_copy_planned_cash(self):
        self.ensure_one()
        if self.projects_id.budget_state == 'fixed':  # сделка в зафиксированном бюджете
            raise_text = _("This project is in fixed budget. Copy deny")
            raise (ValidationError(raise_text))
        elif self.date_cash < date.today():
            raise_text = _("This cash flow is overdue. Copy denied")  # просрочено
            raise (ValidationError(raise_text))
        self.env['project_budget.planned_cash_flow'].browse(self.id).copy({'cash_id': '-'})
