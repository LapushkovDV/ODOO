from odoo import fields, models


class ProcessTemplate(models.Model):
    _inherit = 'document_flow.process.template'

    contract_type_id = fields.Many2one('contract.type', string='Contract Type', ondelete='set null')
    contract_kind_id = fields.Many2one('contract.kind', string='Contract Kind', ondelete='set null')
