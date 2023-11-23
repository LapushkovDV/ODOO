from odoo import api, fields, models
from .document_flow_process import selection_executor_model


class DocumentType(models.Model):
    _name = 'document_flow.document.type'
    _description = 'Document Type'

    name = fields.Char(string='Name', required=True, copy=True)
    sequence_id = fields.Many2one('ir.sequence', string='Document Type Sequence', copy=False, ondelete='restrict',
                                  domain=lambda self: [('code', '=', self._name)])
    access_setting_ids = fields.One2many('document_flow.document.type.accessibility.setting', 'document_type_id',
                                         string='Accessibility Settings')


class DocumentTypeAccessibilitySetting(models.Model):
    _name = 'document_flow.document.type.accessibility.setting'
    _description = 'Document Type Accessibility Setting'

    @api.model
    def _selection_executor_model(self):
        return selection_executor_model()

    document_type_id = fields.Many2one('document_flow.document.type', string='Document Type', index=True, required=True,
                                       copy=True, ondelete='cascade')
    company_id = fields.Many2one('res.company', string='Company', copy=False, required=True,
                                 default=lambda self: self.env.company)
    user_ref = fields.Reference(string='User', selection='_selection_executor_model', copy=False, required=True)
