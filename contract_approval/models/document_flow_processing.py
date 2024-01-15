from odoo import api, fields, models, _


class Processing(models.Model):
    _inherit = 'document_flow.processing'

    @api.model
    def _selection_parent_model(self):
        types = super(Processing, self)._selection_parent_model()
        types.append(('contract.contract', _('Contract')))
        return types

    contract_type_id = fields.Many2one('contract.type', string='Contract Type', copy=False)
    contract_kind_id = fields.Many2one('contract.kind', string='Contract Kind', copy=False)

    @api.depends('parent_ref_type', 'document_kind_id', 'contract_type_id', 'contract_kind_id')
    def _compute_template_id_domain(self):
        for rec in self:
            if rec.parent_ref_type == 'contract.contract':
                domain = [
                    ('model_id.model', '=', rec.parent_ref_type),
                    ('contract_type_id', '=', rec.contract_type_id.id),
                    ('contract_kind_id', '=', rec.contract_kind_id.id)
                ]
                print(domain)
                rec.template_id_domain = domain
            else:
                super(Processing, self)._compute_template_id_domain()
