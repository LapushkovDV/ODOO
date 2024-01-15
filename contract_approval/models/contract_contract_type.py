from odoo import api, fields, models, _


def selection_executor_model():
    return [
        ('res.users', _('User')),
        ('document_flow.role_executor', _('Role'))
    ]


class ContractType(models.Model):
    _inherit = 'contract.type'

    access_setting_ids = fields.One2many('contract.type.accessibility.setting', 'type_id',
                                         string='Accessibility Settings')


class ContractTypeAccessibilitySetting(models.Model):
    _name = 'contract.type.accessibility.setting'
    _description = 'Contract Type Accessibility Setting'

    @api.model
    def _selection_executor_model(self):
        return selection_executor_model()

    type_id = fields.Many2one('contract.type', string='Contract Type', copy=True, index=True, required=True,
                              ondelete='cascade')
    user_ref = fields.Reference(string='User', selection='_selection_executor_model', copy=True, required=True)
    user_id = fields.Many2one('res.users', string='User', compute='_compute_user_id', store=True)
    role_executor_id = fields.Many2one('document_flow.role_executor', string='Group',
                                       compute='_compute_role_executor_id', store=True)

    @api.depends('user_ref')
    def _compute_user_id(self):
        for contract_type in self:
            if type(contract_type.user_ref).__name__ == 'res.users':
                contract_type.user_id = contract_type.user_ref.id
            else:
                contract_type.user_id = False

    @api.depends('user_ref')
    def _compute_role_executor_id(self):
        for document in self:
            if type(document.user_ref).__name__ == 'document_flow.role_executor':
                document.role_executor_id = document.user_ref.id
            else:
                document.role_executor_id = False
