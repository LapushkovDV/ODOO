from odoo import models


class DmsDocumentMixin(models.AbstractModel):
    _name = 'dms.document.mixin'
    _description = "DMS Document creation mixin"

    def _get_document_vals(self, attachment):
        self.ensure_one()
        document_vals = {}
        if self._check_create_documents():
            document_vals = {
                'attachment_id': attachment.id,
                'name': attachment.name or self.display_name,
                'directory_id': self._get_document_directory().id,
                'partner_id': self._get_document_partner().id
            }
        return document_vals

    def _get_document_directory(self):
        return self.env['dms.directory']

    def _get_document_partner(self):
        return self.env['res.partner']

    def _check_create_documents(self):
        return bool(self and self._get_document_directory())
