from odoo import _, models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools import pytz
from datetime import timedelta

class tenders(models.Model):
    _name = 'project_budget.tenders'
    _description = "projects tenders"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name_to_show'
    _check_company_auto = True
    # _rec_names_search = ['project_id', 'essence_project']

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

    projects_id = fields.Many2one('project_budget.projects', required=True,tracking=True, domain = "[('budget_state', '=', 'work')]")
    currency_id = fields.Many2one('res.currency', string='Account Currency',  required = True, copy = True,
                                  default=lambda self: self.env['res.currency'].search([('name', '=', 'RUB')], limit=1),tracking=True)
    project_office_id = fields.Many2one(related='projects_id.project_office_id', readonly=True)
    project_supervisor_id = fields.Many2one(related='projects_id.project_supervisor_id', readonly=True)
    project_manager_id = fields.Many2one(related='projects_id.project_manager_id', readonly=True)
    rukovoditel_project_id = fields.Many2one(related='projects_id.rukovoditel_project_id', readonly=True)

    essence_project = fields.Text(related='projects_id.essence_project', readonly=True)

    date_of_filling_in = fields.Date(string='date_of_filling_in tender', required=True, default=fields.datetime.now(), tracking=True)
    participant_id = fields.Many2one('project_budget.legal_entity_signing',
                                              string='legal_entity_signing a contract from the NCC', required=True,
                                              copy=True, tracking=True)
    auction_number = fields.Char(string='auction_number', default = "",tracking=True)
    url_tender = fields.Text(string='url of tender', default = "",tracking=True)
    customer_organization_id = fields.Many2one(related='projects_id.customer_organization_id', readonly=True)
    contact_information = fields.Text(string='contact_information', default = "",tracking=True)
    name_of_the_purchase = fields.Text(string='name_of_the_purchase', default = "",tracking=True)
    is_need_initial_maximum_contract_price = fields.Boolean(string="is_need_initial_maximum_contract_price", copy=True, default = False)
    initial_maximum_contract_price =fields.Monetary(string='initial_maximum_contract_price',tracking=True)
    participants_offer = fields.Monetary(string='participants_offer',tracking=True, required = True)
    is_need_securing_the_application  = fields.Boolean(string="is_need_securing_the_application", copy=True, default = False)
    securing_the_application = fields.Monetary(string='securing_the_application',tracking=True)
    is_need_contract_security  = fields.Boolean(string="is_need_contract_security", copy=True, default = False)
    contract_security = fields.Monetary(string='contract_security',tracking=True)
    is_need_provision_of_GO  = fields.Boolean(string="is_need_provision_of_GO", copy=True, default = False)
    provision_of_GO = fields.Monetary(string='provision_of_GO',tracking=True)
    is_need_licenses_SRO  = fields.Boolean(string="is_need_licenses_SRO", copy=True, default = False,tracking=True)
    licenses_SRO = fields.Char(string='licenses_SRO',tracking=True)
    project_manager_id = fields.Many2one(related='projects_id.project_manager_id', readonly=True)
    current_status = fields.Many2one('project_budget.tender_current_status', required=True, tracking=True)
    is_need_payment_for_the_victory = fields.Boolean(string="is_need_payment_for_the_victory", copy=True, default = False)
    payment_for_the_victory = fields.Text(string="payment_for_the_victory", copy=True, default ="")
    tender_comments_ids = fields.One2many(comodel_name='project_budget.tender_comments',inverse_name='tenders_id',string="tenders comments", auto_join=True, copy=True)
    presale_number = fields.Char(string="presale_number", copy=True, default ="")

    attachment_count = fields.Integer(compute='_compute_attachment_count', string='Attachments')

    name_to_show = fields.Char(string='name_to_show', compute='_get_name_to_show')

    @api.depends('date_of_filling_in','customer_organization_id','name_of_the_purchase')
    def _get_name_to_show(self):
        for tender in self:
            tender.name_to_show = tender.date_of_filling_in.strftime('%Y-%m-%d') + '|'+ (tender.customer_organization_id.name or '') + '|' + (tender.name_of_the_purchase[:30] or '')+'...'

    def _compute_attachment_count(self):
        for tender in self:
            tender.attachment_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', self._name),
                ('res_id', '=', tender.id)
            ])

    def action_open_attachments(self):
        self.ensure_one()
        return {
            'name': _('Attachments'),
            'domain': [('res_model', '=', self._name), ('res_id', '=', self.id)],
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,tree,form',
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id),
            'help': """
                <p class="o_view_nocontent_smiling_face">%s</p>
                """ % _("Add attachments for this tender")
        }


    @api.onchange('is_need_initial_maximum_contract_price','is_need_securing_the_application','is_need_contract_security'
                  ,'is_need_provision_of_GO','is_need_licenses_SRO','is_need_payment_for_the_victory')
    def _check_changes_tender(self):
        for row in self:
            if row.is_need_initial_maximum_contract_price ==False : row.initial_maximum_contract_price=0
            if row.is_need_securing_the_application==False : row.securing_the_application=0
            if row.is_need_contract_security ==False : row.contract_security =0
            if row.is_need_provision_of_GO ==False : row.provision_of_GO = 0
            if row.is_need_licenses_SRO ==False : row.licenses_SRO = ''
            if row.is_need_payment_for_the_victory == False : row.payment_for_the_victory = ''


class tender_comments(models.Model):
    _name = 'project_budget.tender_comments'
    _description = "projects tender comments"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    tenders_id = fields.Many2one('project_budget.tenders',string='tender id', required=True, copy=True, tracking=True)
    date_comment = fields.Date(string='date of the comment', required=True, default=fields.datetime.now(), tracking=True)
    is_need_type = fields.Boolean(string="is need comment type ", copy=True, default = True)
    type_comment_id = fields.Many2one('project_budget.tender_comments_type',string='tender comments type', copy=True, tracking=True)
    text_comment = fields.Text(string="text of the comment", copy=True, default ="")



